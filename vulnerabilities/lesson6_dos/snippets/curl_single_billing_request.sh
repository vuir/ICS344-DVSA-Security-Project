#!/bin/bash

curl -X POST "$DVSA_API_URL" \
  -H "Content-Type: application/json" \
  -H "authorization: $DVSA_TOKEN" \
  --data-raw '{
    "action":"billing",
    "order-id":"'"$DVSA_ORDER_ID"'",
    "data": {
      "ccn":"4000056655665556",
      "exp":"03/28",
      "cvv":"232"
    }
  }'
