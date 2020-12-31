set -e

sleep 5

echo "[*] creating s3 buckets: s3://visitors"
aws --endpoint-url ${AWS_ENDPOINT} s3 mb s3://visitors

echo "[*] creating sns topics: sns://visit"
aws --endpoint-url ${AWS_ENDPOINT} sns create-topic --name visit

