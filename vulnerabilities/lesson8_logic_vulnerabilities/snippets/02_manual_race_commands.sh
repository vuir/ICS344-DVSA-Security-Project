#!/usr/bin/env bash
# Manual version of the race-condition test.
# Requires TOKEN, API, and ORDER_ID to already be exported.

printf '{"action":"complete","order-id":"%s"}' "$ORDER_ID" > /tmp/lesson8-pay.json
printf '{"action":"update","order-id":"%s","items":{"1014":5}}' "$ORDER_ID" > /tmp/lesson8-update.json

curl -s -X POST "$API" \
  -H "Content-Type: application/json" \
  -H "authorization: $TOKEN" \
  --data-binary @/tmp/lesson8-pay.json > /tmp/pay-result.txt &

sleep 0.05

curl -s -X POST "$API" \
  -H "Content-Type: application/json" \
  -H "authorization: $TOKEN" \
  --data-binary @/tmp/lesson8-update.json > /tmp/update-result.txt &

wait

echo "Pay result:    $(cat /tmp/pay-result.txt)"
echo "Update result: $(cat /tmp/update-result.txt)"
