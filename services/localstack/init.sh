#!/bin/sh

echo "Init localstack s3"

awslocal s3 mb s3://visitors
awslocal sns create-topic --name visit