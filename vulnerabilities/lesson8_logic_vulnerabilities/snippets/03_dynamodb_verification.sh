#!/usr/bin/env bash
# Verify the final order state in DynamoDB.
# Replace ORDER_ID before running, or export it from your shell.

aws dynamodb scan \
  --table-name DVSA-ORDERS-DB \
  --filter-expression "orderId = :oid" \
  --expression-attribute-values '{":oid":{"S":"'"$ORDER_ID"'"}}' \
  --region us-east-1
