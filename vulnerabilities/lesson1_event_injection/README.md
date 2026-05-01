Lesson 1: Event Injection (Remote Code Execution)
=================================================

Overview
-----------

This lesson demonstrates a **Remote Code Execution (RCE)** vulnerability caused by insecure deserialization in a serverless Node.js application.

A malicious payload is injected into the API request and executed inside the AWS Lambda function.

* * * * *

Goal
-------

To show that user input can be executed as code inside the backend, leading to full system compromise.

* * * * *

Requirements
---------------

-   DVSA application access

-   AWS Console (CloudWatch)

-   Postman

-   Browser (DevTools)

* * * * *

Step-by-Step Reproduction
----------------------------

* * * * *

###  Step 1: Get API Endpoint

1.  Go to AWS Console

2.  Open **API Gateway**

3.  Select DVSA API

4.  Copy Invoke URL

See:


[Step 1 api gateway](/vulnerabilities/lesson1_event_injection/evidence/step1_api_gateway.png)


* * * * *

###  Step 2: Prepare Malicious Payload

The payload contains a **serialized function** that will execute inside Lambda.

Example idea:

-   Create file in `/tmp`

-   Read file

-   Print result

```
{
    ”action”: ”˙$$ND˙FUNC$$˙function()– var fs = require(“”fs“”); fs.writeFileSync(“”/tmp/pwned.txt
“”, “”You are reading the contents of my hacked file!“”); var fileData = fs.readFileSync(“”/tmp/
pwned.txt“”, “”utf-8“”); console.error(“”FILE READ SUCCESS: “” + fileData); ˝()”, 
”cart-id”:"" ’
}

```

* * * * *

###  Step 3: Send Request via Postman

1.  POST request:

```
/dvsa/order

```

1.  Header:

```
Content-Type: application/json

```

1.  Inject malicious payload into body


* * * * *

###  Step 4: Observe API Response

-   API returns error

-   Looks like request failed

See:

[Step 4 response](/vulnerabilities/lesson1_event_injection/evidence/step4_response.png)


* * * * *

###  Step 5: Check CloudWatch Logs

1.  Go to AWS Console → CloudWatch

2.  Open Lambda logs

 You will see:

```
FILE READ SUCCESS

```

See:

[Step 5 cloudwatch](/vulnerabilities/lesson1_event_injection/evidence/step5_cloudwatch.png)
* * * * *

Result (Before Fix)
----------------------

-   Backend executed attacker code

-   File operations performed

-   Logs confirm execution

* * * * *

Fix Applied
---------------

-   Removed unsafe deserialization in the backend Lambda function 

-   Replaced:

```
serialize.unserialize

```
See:

[Line code unserialize](/vulnerabilities/lesson1_event_injection/evidence/unserialize.png)

with:

```
JSON.parse

```
See:


[Line code JSON](/vulnerabilities/lesson1_event_injection/evidence/JSON.png)

* * * * *

Verification After Fix
------------------------

1.  Send same malicious payload again

2.  Check CloudWatch

Result:

-   No execution

-   No injected message

See:

[Step 6 fixed logs](/vulnerabilities/lesson1_event_injection/evidence/step6_fixed_logs.png)


* * * * *

Final Result
--------------

| Phase | Behavior |
| --- | --- |
| Before Fix | Code execution |
| After Fix | No execution |
| System | Secure |

* * * * *

Files
--------

-   evidence screenshots

* * * * *

Key Lesson
-------------

User input must **never be executed as code**.\
Unsafe deserialization can lead to full system compromise.

* * * * *