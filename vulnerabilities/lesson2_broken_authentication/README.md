# Lesson 2: Broken Authentication (JWT Forgery)

## How to Use This Folder

1. Read this README from top to bottom.
2. Use the files in `payloads/` to copy clean request bodies and environment-variable templates.
3. Use the scripts in `snippets/` to decode identities, demonstrate JWT payload modification, and document the secure fix.
4. Compare your results with the screenshots in `evidence/`.
5. Apply the fix in `DVSA-ORDER-MANAGER`, then repeat the verification step to confirm the forged token is rejected.

> Do not commit real JWTs or live credentials. The screenshots in this folder are evidence from the lab, and token values are redacted where needed.

---

## 1. Vulnerability Summary

This lesson demonstrates a **Broken Authentication** vulnerability caused by improper validation of JSON Web Tokens (JWT) in the DVSA order system.

The backend trusted identity claims such as `username` and `sub` from the JWT payload without verifying whether the token was genuinely issued by the trusted identity provider. Because of this, an attacker could modify the JWT payload, replace their own identity with another user's identity, and make the backend treat them as the victim user.

The impact is **user impersonation and unauthorized access to another user's private order data** without knowing the victim's password.

The affected component is the `DVSA-ORDER-MANAGER` Lambda function (`order-manager.js`), which originally decoded JWT payload data and trusted it before verifying the token signature.

---

## 2. Root Cause

A JWT has three parts:

```text
header.payload.signature
```

The payload is only Base64URL-encoded. It is not encrypted. Anyone who has a JWT can decode the payload, modify fields, and re-encode it. The part that makes the JWT trustworthy is the **signature**, because the signature proves that the token was issued by the trusted identity provider and has not been modified.

The vulnerable application:

- Decoded the JWT payload using Base64URL decoding
- Trusted `username` and `sub` directly from the decoded payload
- Did not verify the JWT signature against Cognito's public keys before using the claims

### Why the attack works

The attacker starts with a legitimate token from User B. They decode the payload, replace the identity fields with User C's `username` and `sub`, then reuse the original token header and signature. The signature no longer matches the modified payload, but the vulnerable backend does not check that. It reads the modified payload and fetches User C's orders.

This breaks authentication because the server is trusting client-controlled identity data.

---

## 3. Environment

| Item | Value |
|---|---|
| Application | DVSA |
| AWS Region | `us-east-1` |
| API Endpoint | `POST https://d0xsecb8a2.execute-api.us-east-1.amazonaws.com/dvsa/order` |
| Lambda Function | `DVSA-ORDER-MANAGER` |
| File Modified | `order-manager.js` |
| AWS Services | API Gateway, AWS Lambda, Amazon Cognito |
| Tools Used | Browser DevTools, Terminal, `curl`, `python3`, `jq` |

---

## 4. Prerequisites

Before starting:

1. Have access to the DVSA application.
2. Create two normal non-admin accounts:
   - User B: attacker account
   - User C: victim account
3. Make sure both users have at least one order.
4. Install command-line tools.

On macOS:

```bash
brew install curl jq python
```

On Linux:

```bash
sudo apt-get install -y curl python3 jq
```

**Evidence — tool setup:**

![Step 1 - Tool Setup](evidence/step1_tool_setup.png)

---

## 5. Step-by-Step Reproduction

### Step 1: Create Accounts and Place Orders

1. Open the DVSA website.
2. Register and log in as User B.
3. Place at least one order.
4. Log out, then register and log in as User C.
5. Place at least one order for User C.

You will need:

- `TOKEN_B` — User B's JWT
- `TOKEN_C` — User C's JWT
- `ORDER_C` — User C's order ID

---

### Step 2: Capture the API URL and Tokens

1. Log in as User B.
2. Open Browser DevTools → **Network**.
3. Open the Orders page.
4. Click the `/order` request.
5. Copy the request URL and the `Authorization` header.
6. Repeat the same process for User C.

Export the values in your terminal:

```bash
source payloads/environment_variables_template.sh
```

Then edit the placeholders in your terminal session or paste them manually:

```bash
export API="https://d0xsecb8a2.execute-api.us-east-1.amazonaws.com/dvsa/order"
export TOKEN_B="<paste User B JWT here>"
export TOKEN_C="<paste User C JWT here>"
```

**Evidence — API request URL:**

![Step 2 - Request URL](evidence/step2_request_url.png)

**Evidence — TOKEN_B captured from DevTools:**

![Step 2 - Token B Authorization Header](evidence/step2_token_b.png)

**Evidence — TOKEN_C captured from DevTools:**

![Step 2 - Token C Authorization Header](evidence/step2_token_c.png)

Decode both JWT payloads to identify User C's identity fields:

```bash
python3 snippets/decode_jwt_identities.py
```

Copy User C's identity value and export it:

```bash
export VICTIM_USER="<User C username/sub value>"
```

**Evidence — decoded identity values:**

![Step 2 - Decoded Token Identities](evidence/step2_decode_identities.png)

---

### Step 3: Confirm Normal Behavior

Use User B's original token to confirm that User B only sees their own orders:

```bash
curl -s "$API" \
  -H "content-type: application/json" \
  -H "authorization: $TOKEN_B" \
  --data-raw @payloads/orders_request.json | jq
```

**Expected result:** the API returns User B's orders only.

**Evidence — User B orders with legitimate token:**

![Step 3 - User B Orders](evidence/step3_user_b_orders.png)

---

### Step 4: Forge the JWT Payload

Generate a modified token that keeps User B's header and signature but changes the payload identity fields to User C:

```bash
export FAKE_AS_C="$(python3 snippets/forge_jwt_payload.py)"
echo "Forged token length: ${#FAKE_AS_C}"
```

A standalone helper version is also provided:

```bash
python3 broken_auth_test.py
```

**Evidence — forged token generated:**

![Step 4 - JWT Token Forging](evidence/step4_forge_token.png)

---

### Step 5: Use the Forged Token to Access Victim Orders

Send the forged token to the Orders API:

```bash
curl -s "$API" \
  -H "content-type: application/json" \
  -H "authorization: $FAKE_AS_C" \
  --data-raw @payloads/orders_request.json | jq
```

**Expected vulnerable result:** the API returns User C's private orders even though the attacker started from User B's token.

Returned victim order evidence:

```text
order-id: de2c6970-56fc-4b61-8cc5-ef2faf5f4060
total:    44
status:   delivered
```

Export the victim order ID for the next test:

```bash
export ORDER_C="de2c6970-56fc-4b61-8cc5-ef2faf5f4060"
```

**Evidence — victim orders returned using forged token:**

![Step 5 - Victim Orders Returned](evidence/step5_victim_orders_returned.png)

**Evidence — victim order confirmed:**

![Step 5 - Victim Orders Confirmed](evidence/step5_victim_orders_confirmed.png)

---

### Step 6: Attempt Full Order Detail Retrieval

The forged token can also be used to attempt access to detailed order data:

```bash
curl -i "$API" \
  -H "content-type: application/json" \
  -H "authorization: $FAKE_AS_C" \
  --data-raw "{\"action\":\"get\",\"order-id\":\"$ORDER_C\",\"isAdmin\":\"false\"}"
```

The application returned a backend error related to `isAdmin` type handling:

```text
AttributeError: 'bool' object has no attribute 'lower'
```

This error does not fix the authentication issue. The authentication bypass was already proven when the forged token returned User C's order list.

**Evidence — backend error during full order retrieval:**

![Step 6 - Backend Error](evidence/step6_backend_error.png)

---

## 6. Attack Result Summary (Before Fix)

| What was attempted | Result |
|---|---|
| Use User B's original JWT | Succeeded — User B orders returned |
| Modify JWT payload identity fields | Succeeded |
| Use forged token to access User C orders | Succeeded — victim orders returned |
| Retrieve full victim order details | Partial — blocked by separate backend type-handling error |

The core issue is confirmed: the backend accepted a tampered JWT and trusted the modified identity claims.

---

## 7. Fix Strategy

The fix must be applied inside `DVSA-ORDER-MANAGER` in `order-manager.js`:

- Verify the JWT signature using Cognito's JWKS public keys before trusting claims.
- Validate required claims such as `iss`, `exp`, and `token_use`.
- Reject tampered, expired, malformed, or unverifiable tokens with HTTP `401`.
- Never use `username`, `sub`, or other JWT fields for authorization before verification succeeds.

---

## 8. Code / Config Changes

**Location:** `DVSA-ORDER-MANAGER` → `order-manager.js`

### Before: vulnerable JWT handling

```javascript
// Split token manually, base64 decode payload, trust claims directly
var token_sections = auth_header.split('.');
var auth_data = jose.util.base64url.decode(token_sections[1]);
var token = JSON.parse(auth_data);
var user = token.username;
```

Snippet file:

```text
snippets/vulnerable_jwt_decode_snippet.js
```

### After: secure JWT verification

The fix adds helper functions to fetch Cognito public keys, verify the JWT signature, and validate claims before reading the user identity.

Snippet file:

```text
snippets/jwt_verification_fix_snippet.js
```

**Evidence — JWT helper functions added:**

![Fix - JWT Helper Functions](evidence/fix_jwt_helper_functions.png)

After verification succeeds, the backend reads identity from verified claims only:

```javascript
verifyCognitoJwt(jwt).then((claims) => {
    var user = claims.username || claims["cognito:username"] || claims.sub;
    // Continue normal processing only after verification succeeds.
}).catch((e) => {
    console.log("JWT verify failed:", e);
    return callback(null, resp(401, { status: "err", msg: "invalid token" }));
});
```

**Evidence — verified claims handling:**

![Fix - JWT Claims Validation](evidence/fix_jwt_claims_validation.png)

**Evidence — invalid token response path:**

![Fix - Invalid Token Response Code](evidence/fix_invalid_token_response.png)

---

## 9. Verification After Fix

Repeat the same request with the forged token:

```bash
curl -s "$API" \
  -H "content-type: application/json" \
  -H "authorization: $FAKE_AS_C" \
  --data-raw @payloads/orders_request.json | jq
```

**Expected result after fix:**

```json
{
  "status": "err",
  "msg": "invalid token"
}
```

**Evidence — forged token rejected after fix:**

![Step 8 - Post-Fix Invalid Token Response](evidence/step8_post_fix_invalid_token.png)

**What changed:** before the fix, the backend trusted decoded payload claims directly. After the fix, `verifyCognitoJwt()` verifies the signature first. Since the forged token has a modified payload and mismatched signature, verification fails and the request is rejected before any user data is returned.

---

## 10. Security Analysis

### Intended Logic

The intended authentication flow is:

```text
Browser → Cognito login → signed JWT issued
Browser → API Gateway → Lambda verifies JWT → DynamoDB returns only that user's orders
```

Security rules:

- JWT signature must be verified before claims are trusted.
- User identity must not come from an unverified client-controlled payload.
- A token with a mismatched signature must be rejected immediately.
- Each user should only access their own order data.

### Table 1 — Intended vs. Observed Behavior

| Vulnerability | Intended Rule(s) | Artifacts Used | Normal Behavior Evidence | Exploit Behavior Evidence |
|---|---|---|---|---|
| Broken Authentication (JWT Forgery) | Only a valid, cryptographically verified JWT should determine user identity. User B must only access User B's orders. | Browser DevTools, captured JWTs, terminal output, forged token, Lambda source code screenshots | User B's valid token returned only User B's own orders (`step3_user_b_orders.png`) | Forged token returned User C's private order list (`step5_victim_orders_returned.png`) |

### Table 2 — Deviation Analysis and Fix

| Vulnerability | Why This Is a Deviation | Deviation Class | Fix Applied | Post-Fix Verification | Latency |
|---|---|---|---|---|---|
| Broken Authentication (JWT Forgery) | The backend trusted attacker-controlled JWT payload claims without verifying the token signature. This allowed impersonation by modifying `username` and `sub`. | Intentional Misuse / Security-Relevant Abuse | Added `verifyCognitoJwt()` in `order-manager.js` using Cognito JWKS public keys. Claims are trusted only after signature verification succeeds. | Forged token returns `{"status":"err","msg":"invalid token"}` and victim data is no longer returned (`step8_post_fix_invalid_token.png`) | ~120 ms / ~128 ms |

---

## 11. Lessons Learned

JWT payloads are not secret. They are easy to decode and modify because they are only Base64URL-encoded. The signature is what protects the token from tampering.

The mistake in this lesson was treating decoded JWT claims as trusted identity. That allowed an attacker to choose who they wanted to be by editing the token payload.

Authentication must be verified cryptographically on the server side. In this case, the Lambda should verify the JWT against Cognito's public keys before reading `username`, `sub`, or any other identity claim.

The main lesson is: **never trust JWT claims until the token signature has been verified**.

---

## Repository Structure

```text
lesson2_broken_authentication/
│
├── README.md
├── broken_auth_test.py
├── evidence/
│   ├── step1_tool_setup.png
│   ├── step2_request_url.png
│   ├── step2_token_b.png
│   ├── step2_token_c.png
│   ├── step2_decode_identities.png
│   ├── step3_user_b_orders.png
│   ├── step4_forge_token.png
│   ├── step5_victim_orders_returned.png
│   ├── step5_victim_orders_confirmed.png
│   ├── step6_backend_error.png
│   ├── fix_jwt_helper_functions.png
│   ├── fix_jwt_claims_validation.png
│   ├── fix_invalid_token_response.png
│   └── step8_post_fix_invalid_token.png
├── payloads/
│   ├── orders_request.json
│   ├── get_order_request_template.json
│   └── environment_variables_template.sh
└── snippets/
    ├── decode_jwt_identities.py
    ├── forge_jwt_payload.py
    ├── vulnerable_jwt_decode_snippet.js
    ├── jwt_verification_fix_snippet.js
    └── invalid_token_response_snippet.js
```
