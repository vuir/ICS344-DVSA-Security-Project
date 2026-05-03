#!/usr/bin/env bash

# Lesson 2 - Broken Authentication environment template
# Replace placeholders with temporary values captured from your DVSA lab session.
# Do not commit real JWTs to GitHub.

export API="https://d0xsecb8a2.execute-api.us-east-1.amazonaws.com/dvsa/order"
export TOKEN_B="<paste User B JWT here>"
export TOKEN_C="<paste User C JWT here>"
export VICTIM_USER="<paste User C username/sub here>"
export ORDER_C="<paste User C order-id here>"
