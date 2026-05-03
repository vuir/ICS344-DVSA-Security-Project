# Lesson 6: Denial of Service (DoS)

## How to Use This Folder

1. Read this README from top to bottom.
2. Follow the reproduction steps in Section 5.
3. Use the sample request bodies in the `payloads/` folder.
4. Use the helper script `dos_test.py` only in the authorized DVSA lab environment.
5. Compare your results with the screenshots in the `evidence/` folder.
6. Apply the infrastructure fixes shown in Section 8.
7. Repeat the verification steps in Section 9 to confirm the vulnerability is mitigated.

---

## 1. Vulnerability Summary

This lesson demonstrates a **Denial of Service (DoS)** vulnerability in the DVSA billing workflow.

The billing endpoint accepts repeated concurrent requests without enough request throttling or traffic filtering. By sending a high number of billing requests at the same time, the backend becomes unstable and begins returning server errors.

The affected components are:

- API Gateway order endpoint
- Billing action in the DVSA order workflow
- Lambda backend processing
- DynamoDB order update flow

The main impact is reduced availability. During the attack, legitimate users may experience slow responses, failed payments, and backend errors such as `500 Internal Server Error` or `502 Bad Gateway`.

---

## 2. Root Cause

The vulnerability exists because the backend does not properly control request volume before requests reach the application logic.

The main causes are:

- **No strict API Gateway throttling** before the fix.
- **No AWS WAF rate-based blocking** before the fix.
- **High burst allowance** that allowed many requests to reach Lambda at the same time.
- **No application-level protection** against repeated billing attempts.

### Why the attack works

The billing endpoint is designed for a normal user to send one billing request for one order. However, before the fix, the API Gateway stage allowed a very high rate and burst value. This meant that a single client could send many billing requests at the same time.

When the script starts many concurrent threads, API Gateway forwards the requests to Lambda. Lambda and the backend order workflow become overloaded, causing mixed responses:

- Some requests return normal `200` responses.
- Some requests return `500 Internal Server Error`.
- Some requests return `502 Bad Gateway`.
- Response time increases.

This shows that the system lacks effective request throttling and rate protection.

---

## 3. Environment

| Item | Value |
|---|---|
| Application | DVSA |
| AWS Region | `us-east-1` |
| API Endpoint | `POST https://<api-id>.execute-api.us-east-1.amazonaws.com/dvsa/order` |
| Affected Action | `billing` |
| AWS Services | API Gateway, AWS Lambda, Amazon DynamoDB, AWS WAF |
| Tools Used | Python 3, `requests`, `threading`, Postman, Browser DevTools, AWS Console |

**Evidence — API Gateway settings before and after the fix:**

![API Gateway before fix](evidence/api_gateway_before.png)

![API Gateway after fix](evidence/api_gateway_after.png)

---

## 4. Prerequisites

Before starting:

1. Have access to the authorized DVSA lab environment.
2. Have a valid normal user account.
3. Have a valid order ready for billing.
4. Have Browser DevTools or Postman available to capture the request.
5. Have Python 3 installed.
6. Install the required Python package:

```bash
pip install -r
```

**Estimated time to reproduce:** 10-15 minutes if the DVSA environment is already deployed.

The helper script `dos_test.py` is sanitized and uses placeholders. Do not commit real authorization tokens or real private environment values to GitHub.

---

## 5. Step-by-Step Reproduction

### Step 1: Create a New Order

1. Open the DVSA application.
2. Log in using a normal user account.
3. Add a product to the cart.
4. Continue to checkout.
5. Stop at the billing/payment step so you can capture a valid billing request.

---

### Step 2: Capture a Valid Billing Request

1. Open Browser DevTools.
2. Go to the **Network** tab.
3. Perform or prepare the billing action.
4. Find the `POST /dvsa/order` request.
5. Copy the following values:
   - API endpoint URL
   - `Authorization` header value
   - `order-id` from the request body

Set the values as environment variables:

```bash
export DVSA_API_URL="https://<api-id>.execute-api.us-east-1.amazonaws.com/dvsa/order"
export DVSA_TOKEN="<paste_token_here>"
export DVSA_ORDER_ID="<paste_order_id_here>"
```

---

### Step 3: Verify a Single Request Works

Before running the load script, verify that one normal billing request reaches the endpoint.

Example request body:

```json
{
  "action": "billing",
  "order-id": "<ORDER_ID>",
  "data": {
    "ccn": "4000056655665556",
    "exp": "03/28",
    "cvv": "232"
  }
}
```

A normal single request returns a controlled response, such as:

```json
{"status":"err","msg":"order already made"}
```

This confirms that the endpoint works under normal load.

**Evidence:**

![Step 3 - Normal billing request](evidence/step3_normal_request.png)

---

### Step 4: Run the DoS Test Script

The helper script `dos_test.py` sends many billing requests concurrently.

Run it with the default thread count:

```bash
python dos_test.py
```

Or set a specific thread count:

```bash
export DVSA_THREAD_COUNT="200"
python dos_test.py
```

The script uses the values from these environment variables:

```bash
DVSA_API_URL
DVSA_TOKEN
DVSA_ORDER_ID
DVSA_THREAD_COUNT
```

---

### Step 5: Observe the Attack Result Before the Fix

Expected vulnerable behavior:

- Some requests return `200`.
- Many requests return `500` or `502`.
- The backend becomes unstable.
- Response latency increases.

This confirms that the backend receives more traffic than it can safely handle.

**Evidence:**

![Step 5 - DoS attack output before fix](evidence/step5_dos_attack_output.png)

---

## 6. Attack Result Summary (Before Fix)

| What was attempted | Result |
|---|---|
| Send one normal billing request | Succeeded with controlled response |
| Send many concurrent billing requests | Succeeded in reaching backend |
| Backend stability under load | Failed |
| Error responses observed | `500` and `502` |
| Rate limiting protection | Not sufficient before fix |

The attack proves that the endpoint could be overloaded by repeated concurrent requests. This is a security issue because availability is part of system security.

---

## 7. Fix Strategy

The fix should be applied at the infrastructure layer before traffic reaches Lambda.

Recommended mitigation:

- **Enable API Gateway throttling** to limit request rate and burst size.
- **Attach AWS WAF to the API Gateway stage**.
- **Create a WAF rate-based rule** to block clients that exceed the allowed request threshold.
- **Keep normal user traffic working** while blocking abusive traffic.
- **Monitor logs and metrics** to tune thresholds safely.

This lesson uses defense in depth: API Gateway throttling reduces the request rate, and AWS WAF blocks abusive clients.

---

## 8. Code / Config Changes

No Lambda application code was required for the main fix. The mitigation was applied through API Gateway and AWS WAF configuration.

### Config Change 1: API Gateway Stage Throttling

**Location:** API Gateway → APIs → DVSA API → Stages → Stage settings

| Setting | Before | After |
|---|---:|---:|
| Rate | `10000` | `5` |
| Burst | `5000` | `10` |

**Before fix:**

![API Gateway before fix](evidence/api_gateway_before.png)

**After fix:**

![API Gateway after fix](evidence/api_gateway_after.png)

---

### Config Change 2: AWS WAF Rate-Based Rule

A WAF rate-based rule was applied to block clients sending too many requests in a short time window.

Example rule:

```text
Rule name: BlockHighRateIPs
Type: Rate-based rule
Limit: 100 requests per 5 minutes per IP
Action: Block
Associated resource: API Gateway stage
```

**Summary of all changes:**

- Reduced API Gateway stage rate limit.
- Reduced API Gateway stage burst limit.
- Added AWS WAF protection.
- Added a rate-based blocking rule.
- Preserved normal single-request billing behavior.

---

## 9. Verification After Fix

After applying the fixes, run the same helper script again:

```bash
python dos_test.py
```

Expected result after fix:

```json
{"message":"Forbidden"}
```

Most or all high-rate requests should return `403 Forbidden`, showing that the flood is blocked before it reaches the backend.

**Evidence — WAF blocks high-rate requests:**

![WAF blocks high-rate requests](evidence/waf_block.png)

**What changed:** Before the fix, the backend received the high-rate request burst and returned mixed `500`/`502` failures. After the fix, WAF and API Gateway throttling stop abusive traffic earlier, reducing backend instability.

---

## 10. Security Analysis

### Intended Logic

Under normal conditions, a user should send one billing request per order. The expected flow is:

```text
Browser → API Gateway → Lambda billing logic → DynamoDB order update
```

**Security rules the system must enforce:**

- The system must limit excessive requests from one client.
- The billing endpoint must remain available for legitimate users.
- Backend resources should not be exposed directly to uncontrolled request bursts.
- Abusive traffic should be blocked before it reaches Lambda.

---

### Table 1 — Intended vs. Observed Behavior

| Vulnerability | Intended Rule(s) | Artifacts Used | Normal Behavior Evidence | Exploit Behavior Evidence |
|---|---|---|---|---|
| Denial of Service through concurrent billing requests | The system must limit excessive requests and prevent backend resource exhaustion. | Postman request, Python helper script, API Gateway settings, WAF response output | A single billing request returns a controlled `200` response (`step3_normal_request.png`) | 200 concurrent requests cause mixed `500`/`502` errors and backend instability (`step5_dos_attack_output.png`) |

---

### Table 2 — Deviation Analysis and Fix

| Vulnerability | Why This Is a Deviation | Deviation Class | Fix Applied | Post-Fix Verification | Latency |
|---|---|---|---|---|---|
| Denial of Service through concurrent billing requests | The system allowed excessive concurrent requests to reach backend services, violating the rule that request volume should be controlled to preserve availability. | Accidental Misconfiguration / Security-Relevant Abuse | API Gateway throttling was lowered to Rate `5` and Burst `10`; AWS WAF rate-based blocking was added | Re-running the flood returns `403 Forbidden`, showing the traffic is blocked before backend overload | Not measured |

---

## 11. Lessons Learned

This lesson shows that serverless applications still need availability protections. Lambda can scale quickly, but that does not mean every request should be allowed to reach the backend.

The core issue was not a code bug inside the billing logic. The issue was missing infrastructure-level protection. Without throttling and WAF, a single client could send many requests at once and cause backend instability.

The main takeaway is that DoS protection should be designed before deployment. API Gateway throttling and AWS WAF rate-based rules provide an important first layer of defense by filtering abusive traffic before it consumes backend resources.

---

## Repository Structure

```text
lesson6_dos/
│
├── README.md
├── dos_test.py
├── evidence/
│   ├── api_gateway_before.png
│   ├── api_gateway_after.png
│   ├── step3_normal_request.png
│   ├── step5_dos_attack_output.png
│   └── waf_block.png
├── payloads/
│   ├── billing_request.json
│   └── high_load_billing_payload.json
└── snippets/
    ├── api_gateway_throttling_settings.md
    ├── curl_single_billing_request.sh
    ├── run_dos_test.md
    └── waf_rate_based_rule.md
```
