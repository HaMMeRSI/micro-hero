import boto3
import os
import time
import json
import logging
import random

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')


def run():
    sns = boto3.client('sns', endpoint_url=os.getenv('AWS_ENDPOINT'))
    topic_arn = os.getenv('SNS_TOPIC_ARN', 'arn:aws:sns:us-east-1:000000000000:micro-hero')

    visitors = [
                   'https://d-id-public-bucket.s3.us-west-2.amazonaws.com/micro-hero/joker-1.jpg',
                   'https://d-id-public-bucket.s3.us-west-2.amazonaws.com/micro-hero/joker-2.jpg',
                   'https://d-id-public-bucket.s3.us-west-2.amazonaws.com/micro-hero/joker-1.jpg',
                   'https://d-id-public-bucket.s3.us-west-2.amazonaws.com/micro-hero/batman.jpg',
                   'https://d-id-public-bucket.s3.us-west-2.amazonaws.com/micro-hero/bat-1.jpg',
                   'https://d-id-public-bucket.s3.us-west-2.amazonaws.com/micro-hero/joker-1.jpg',
                   'https://d-id-public-bucket.s3.us-west-2.amazonaws.com/micro-hero/joker-1.jpg',
                   'https://d-id-public-bucket.s3.us-west-2.amazonaws.com/micro-hero/bat-2.jpg',
                   'https://d-id-public-bucket.s3.us-west-2.amazonaws.com/micro-hero/joker-2.jpg',
                   'https://d-id-public-bucket.s3.us-west-2.amazonaws.com/micro-hero/batman-with-mask.jpg',
                   'https://d-id-public-bucket.s3.us-west-2.amazonaws.com/micro-hero/batman.jpg'
               ] * 10

    for id_, visitor in enumerate(visitors):
        time.sleep(random.randint(2, 5) * 3)
        message = json.dumps({'id': id_, 'visitor_url': visitors[id_]}, indent=4)
        subject = 'DETECT'
        logging.info(f'[*] Subject:{subject}\n{message}')
        sns.publish(TopicArn=topic_arn, Subject=subject, Message=message)


if __name__ == '__main__':
    run()
