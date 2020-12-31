import flask
from flask import request
import tempfile
import os
import json
import boto3
from botocore.exceptions import ClientError
import logging
import requests
from app.recognizer import BatmanRecognizer


def subscribe(app):
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')
    recognize_endpoint = os.getenv('RECOGNIZE_ENDPOINT')
    aws_endpoint = os.getenv('AWS_ENDPOINT')

    # get aws clients
    app.s3 = boto3.client('s3', endpoint_url=aws_endpoint)
    app.sns = boto3.client('sns', endpoint_url=aws_endpoint)
    app.recognizer = BatmanRecognizer(os.getenv('BATMAN_IMG'))
    app.topic_arn = os.getenv('SNS_TOPIC_ARN')

    # subscribe
    logging.info(f'[*] subscribing sns topic {app.topic_arn} to {recognize_endpoint}')
    app.sns.subscribe(TopicArn=app.topic_arn, Protocol='http', Endpoint=recognize_endpoint)


APP = flask.Flask('recognize')
APP.config["DEBUG"] = False
subscribe(APP)


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
        requests.get(data['SubscribeURL'].replace('http://localhost', 'http://localstack'))

    # handle notification
    elif header == 'Notification':
        subject = data.get('Subject')
        if subject == 'FR':
            raw_message = data.get('Message')
            try:
                message = json.loads(raw_message)
                _process_fr(message)
            except (KeyError, AssertionError, json.JSONDecodeError):
                logging.error(f'[!] FR message is invalid '
                              f'\n expected: {{"id": xxx, "visitor_url": s3://visitors/.., "detection": [T, R, B, L]}}'
                              f'\n got: {raw_message}')
                return flask.jsonify('Error ❌')
            except ClientError:
                logging.error(f'[!] could not read image from s3'
                              f'\n got: {raw_message}')
                return flask.jsonify('Error ❌')
    return flask.jsonify('OK ✅')


def _process_fr(message):
    visitor = message['visitor_url']
    detection = message['detection']
    suffix = visitor.rsplit('.', maxsplit=1)[-1]
    with tempfile.NamedTemporaryFile(suffix=suffix) as local_visitor:
        # recognize
        bucket, key = visitor.replace('s3://', '').split('/', maxsplit=1)
        APP.s3.download_file(bucket, key, local_visitor.name)
        is_batman = APP.recognizer.is_batman(local_visitor.name, detection)

        # create new message
        message = json.dumps({'id': message['id'], 'visitor_url': visitor}, indent=4)
        subject = 'OPEN' if is_batman else 'PROTECT'
        logging.info(f'[*] Subject:{subject}\n{message}')
        APP.sns.publish(TopicArn=APP.topic_arn, Subject=subject, Message=message)


APP.run(host='0.0.0.0', port=5000, threaded=True)
