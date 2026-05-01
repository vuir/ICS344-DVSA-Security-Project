# Lesson 10: Unhandled Exceptions

## Vulnerability Summary

This lesson demonstrates an Unhandled Exceptions vulnerability in the DVSA serverless application. A malformed Lambda test event caused the backend function to crash and expose internal error details.

The issue happened in the `DVSA-ORDER-GET` Lambda function when invalid input reached `get_order.py` without proper validation.

## Root Cause

The backend assumed that the `isAdmin` value would always be a string and called `.lower()` on it. When `isAdmin` was sent as a boolean value, the function crashed with an `AttributeError`.

Main causes:

- Missing input validation
- Unsafe type handling
- Lack of controlled exception handling
- Internal error details exposed in the Lambda execution result

## Environment

- Application: DVSA
- Region: `us-east-1`
- Component: `DVSA-ORDER-GET`
- File: `get_order.py`
- Tools: AWS Lambda Console, Lambda Test Event, CloudWatch Logs

## Reproduction Steps

1. Opened AWS Lambda in the AWS Console.
2. Selected the function `DVSA-ORDER-GET`.
3. Created a new Lambda test event named `lesson10-test`.
4. Used a malformed payload with `orderId` as null and `isAdmin` as a boolean.
5. Executed the test event.
6. The function generated an internal exception instead of safely rejecting the request.

Payload used:

`{"orderId":null,"isAdmin":true}`

## Evidence

The malformed input triggered the following error:

`AttributeError: 'bool' object has no attribute 'lower'`

The Lambda execution result exposed internal details such as:

- `errorMessage`
- `errorType`
- stack trace
- internal file path `/var/task/get_order.py`

This proves that invalid input was processed without safe validation or controlled exception handling.

All evidence screenshots are stored in the `evidence/` folder.

## Fix Strategy

The fix should be applied inside `get_order.py` in the `DVSA-ORDER-GET` Lambda function.

The function should validate the type of `isAdmin` before calling `.lower()` and should handle malformed input safely. Invalid requests should return a controlled error instead of exposing internal stack traces.

Recommended fixes:

- Validate input types before processing
- Do not call `.lower()` on untrusted values without checking the type
- Return generic client-safe error messages
- Log detailed errors internally only

## Code Change

Safe type handling was added for the `isAdmin` value before processing it.

Example secure logic:

`is_admin = str(is_admin).lower() == "true"`

This prevents the function from crashing when `isAdmin` is sent as a boolean value.

## Verification After Fix

After applying the fix, the same malformed test event was executed again.

Before the fix, the function failed with:

`AttributeError: 'bool' object has no attribute 'lower'`

After the fix, this specific error no longer occurred. The function handled the `isAdmin` value safely and did not trigger the previous unsafe type-handling failure.

A new DynamoDB validation error may still appear because `orderId` is null, but the original unhandled exception was removed.

Post-fix verification screenshots are stored in the `evidence/` folder.

## Security Analysis

| Item | Description |
|---|---|
| Vulnerability | Unhandled Exceptions |
| Intended Rule | Invalid input must be validated safely without exposing internal backend details |
| Exploit Behavior | Malformed input triggered `AttributeError` and exposed stack trace |
| Root Cause | Unsafe type handling and missing validation |
| Fix | Added safe type validation in `get_order.py` |
| Post-Fix Result | Original `AttributeError` no longer occurs |

## Lessons Learned

Input values should never be trusted, even simple fields such as `isAdmin`.

Serverless functions must validate malformed input before processing it and return safe error messages. Exposing stack traces, file paths, and internal implementation details can help attackers understand the backend and prepare further attacks.

The main lesson is that safe input validation and controlled exception handling are required to protect backend logic and reduce information disclosure.