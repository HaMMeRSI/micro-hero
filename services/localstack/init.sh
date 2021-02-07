#!/bin/sh
# This file should be in LF format line separators - even in windows!

echo "[!] Init localstack s3://visitors"
awslocal s3 mb s3://visitors

echo "[!] Init localstack sns://visit"
awslocal sns create-topic --name visit

echo "|================================================================================================"
echo "| Localstack is READY for Batman"
echo "| Make sure all your code runs after this line >>>"
echo "|================================================================================================"
