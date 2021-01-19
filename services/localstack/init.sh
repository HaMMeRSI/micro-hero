#!/bin/sh

echo "[!] Init localstack s3://visitors"
awslocal s3 mb s3://visitors

echo "[!] Init localstack sns://visit"
awslocal sns create-topic --name visit

echo "[!] Localstack READY for Batman..."