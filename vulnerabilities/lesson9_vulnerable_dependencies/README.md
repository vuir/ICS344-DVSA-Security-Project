Lesson 9: Vulnerable Dependencies
=================================

Overview
-----------

This lesson demonstrates how using an **insecure third-party dependency** can lead to a critical vulnerability such as **Remote Code Execution (RCE)**.

The issue originates from a deserialization library that executes user-controlled input, allowing attackers to run arbitrary code inside the AWS Lambda function.

* * * * *

Relation to Lesson 1
-----------------------

This vulnerability is directly related to **Lesson 1: Event Injection**, where the actual exploitation steps and detailed analysis are demonstrated.

For full reproduction steps, payload details, and evidence, refer to:

[Lesson 1: Event Injection](../lesson1_event_injection/README.md)

* * * * *

Key Idea
-----------

The vulnerability exists because:

-   A third-party library allows execution of serialized functions

-   User input is treated as executable code instead of data

Even if the application logic is correct, using unsafe dependencies introduces serious risks.

* * * * *

Impact
---------

-   Remote Code Execution (RCE)

-   Execution of attacker-controlled code inside Lambda

-   Potential access to sensitive resources

* * * * *

Fix Strategy
----------------

-   Remove unsafe deserialization library

-   Replace with safe parsing (`JSON.parse`)

-   Validate all incoming input

-   Regularly audit and update dependencies

* * * * *

Key Lesson
-------------

Security is not only about your code ---\
**your dependencies can break your system too.**

Always:

-   Review third-party libraries

-   Avoid unsafe deserialization

-   Treat all user input as data

* * * * *