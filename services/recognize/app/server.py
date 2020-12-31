import flask
from flask import request
import tempfile
import os
import s3fs
import json
import boto3
import logging
import requests
from app.recognizer import BatmanRecognizer

APP = flask.Flask('recognize')
APP.config["DEBUG"] = False


@APP.before_first_request
def subscribe():
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')
    recognize_endpoint = os.getenv('RECOGNIZE_ENDPOINT')
    aws_endpoint = os.getenv('AWS_ENDPOINT')
    APP.s3 = s3fs.S3FileSystem(client_kwargs={'endpoint_url': aws_endpoint})
    APP.sns = boto3.client('sns', endpoint_url=aws_endpoint)
    APP.recognizer = BatmanRecognizer(os.getenv('BATMAN_IMG'))
    APP.topic_arn = os.getenv('SNS_TOPIC_ARN')

    logging.info(f'[*] subscribing sns topic {APP.topic_arn} to {recognize_endpoint}')
    APP.sns.subscribe(TopicArn=APP.topic_arn, Protocol='http', Endpoint=recognize_endpoint)


@APP.route('/sns', methods=['GET', 'POST', 'PUT'])
def sns():
    try:
        data = json.loads(request.data)
        header = request.headers.get('X-Amz-Sns-Message-Type')
    except (json.JSONDecodeError, KeyError):
        return flask.jsonify('Error ❌')

    if header == 'SubscriptionConfirmation' and 'SubscribeURL' in data:
        requests.get(data['SubscribeURL'].replace('http://localhost', 'http://localstack'))

    elif header == 'Notification':
        message = json.loads(data.get('Message'))
        subject = data.get('Subject')

        if subject == 'FR':
            try:
                _process_fr(message)
            except (KeyError, AssertionError):
                logging.error(f'[!] UPLOAD message is invalid '
                              f'\n expected: {{"id": xxx, "visitor_url": s3://visitors/.., "detection": [T, L, B, R]}}'
                              f'\n got: {message}')
                return flask.jsonify('Error ❌')
    return flask.jsonify('OK ✅')


def _process_fr(message):
    visitor = message['visitor_url']
    detection = message['detection']
    suffix = visitor.rsplit('.', maxsplit=1)[-1]
    with tempfile.NamedTemporaryFile(suffix=suffix) as local_visitor:
        APP.s3.download(visitor, local_visitor.name)
        is_batman = APP.recognizer.is_batman(local_visitor, detection)

        message = json.dumps({'id': message['id']}, indent=4)
        subject = 'OPEN' if is_batman else 'PROTECT'
        logging.info(f'[*] Subject:{subject}\n{message}')
        APP.sns.publish(TopicArn=APP.topic_arn, Subject=subject, Message=message)


@APP.route('/healthy', methods=['GET'])
def healthy():
    return flask.jsonify('Healthy 🩺')


APP.run(host='0.0.0.0', port=5000, threaded=True)
