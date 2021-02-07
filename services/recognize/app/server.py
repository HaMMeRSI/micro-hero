import tempfile
import os
import json
import boto3
import logging
import requests
import time
import threading

import flask
from flask import request
from botocore.exceptions import ClientError

from app.recognizer import BatmanRecognizer

APP = flask.Flask('recognize')
APP.config["DEBUG"] = False


def subscribe():
    time.sleep(2)
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')
    recognize_endpoint = os.getenv('RECOGNIZE_ENDPOINT')
    aws_endpoint = os.getenv('AWS_ENDPOINT')

    # get aws clients
    APP.s3 = boto3.client('s3', endpoint_url=aws_endpoint)
    APP.sns = boto3.client('sns', endpoint_url=aws_endpoint)
    APP.recognizer = BatmanRecognizer(os.getenv('BATMAN_IMG'))
    APP.topic_arn = os.getenv('SNS_TOPIC_ARN')

    # subscribe
    logging.info(f'[*] subscribing sns topic {APP.topic_arn} to {recognize_endpoint}')
    APP.sns.subscribe(TopicArn=APP.topic_arn, Protocol='http', Endpoint=recognize_endpoint)


@APP.route('/sns', methods=['GET', 'POST', 'PUT'])
def sns():
    try:
        data = json.loads(request.data)
        header = request.headers.get('X-Amz-Sns-Message-Type')
    except (json.JSONDecodeError, KeyError):
        logging.error(f'Could not understand request {request.data}')
        return flask.jsonify('Error ❌')

    # confirm subscription
    if header == 'SubscriptionConfirmation' and 'SubscribeURL' in data:
        subscription_url = data['SubscribeURL'].replace('http://localhost', 'http://localstack')
        logging.info(f'Confirming subscription: {subscription_url}')
        requests.get(subscription_url)

    # handle notification
    elif header == 'Notification':
        subject = data.get('Subject')
        raw_message = data.get('Message')
        message = json.loads(raw_message)
        if subject == 'FR':
            try:
                _process_fr(message)
            except (KeyError, AssertionError, json.JSONDecodeError):
                logging.error(f'[!] FR message is invalid '
                              f'\n expected: '
                              f'\n   {{"id": xxx, "visitor_url": s3://visitors/.../*.jpg, "detection": [T, R, B, L]}}'
                              f'\n got: '
                              f'\n   {raw_message}')
                return flask.jsonify('Error ❌')
            except ClientError:
                logging.error(f'[!] could not read image from s3'
                              f'\n got: {raw_message}')
                return flask.jsonify('Error ❌')
        else:
            logging.info(f'[*] Subject:{subject}\n{message} - ignored!')

    return flask.jsonify('OK ✅')


def _process_fr(message):
    visitor = message['visitor_url']
    detection = message['detection']
    assert visitor.endswith('.jpg')
    assert isinstance(detection, list)
    suffix = visitor.rsplit('.', maxsplit=1)[-1]
    with tempfile.NamedTemporaryFile(suffix=f'.{suffix}') as local_visitor:
        # recognize
        bucket, key = visitor.replace('s3://', '').split('/', maxsplit=1)
        APP.s3.download_file(bucket, key, local_visitor.name)
        is_batman = APP.recognizer.is_batman(local_visitor.name, tuple(detection))

        # create new message
        message = json.dumps({'id': message['id'], 'visitor_url': visitor}, indent=4)
        subject = 'OPEN' if is_batman else 'PROTECT'
        logging.info(f'[*] Subject:{subject}\n{message}')
        APP.sns.publish(TopicArn=APP.topic_arn, Subject=subject, Message=message)


delayed_subscriber = threading.Thread(target=subscribe)  # 2 seconds delay subscribe
delayed_subscriber.start()
APP.run(host='0.0.0.0', port=5000, threaded=True)
