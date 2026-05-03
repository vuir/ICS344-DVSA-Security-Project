#!/usr/bin/env bash

# Verify the order record directly in DynamoDB after exploitation.
# Expected vulnerable result: orderStatus becomes paid.

aws dynamodb get-item \
  --table-name DVSA-ORDERS-DB \
  --region us-east-1 \
  --key file://payloads/dynamodb_get_item_key.json \
  --output json
