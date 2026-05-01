# Lesson 5: Broken Access Control

## Vulnerability Summary

This lesson demonstrates a Broken Access Control vulnerability in the DVSA order workflow. A normal authenticated user was able to reach the administrative update action `admin-update-orders` and change an order status without administrator privileges.

The impact is that an unprivileged user can bypass the normal payment workflow and make an order appear as paid.

## Root Cause

The backend allowed access to a privileged administrative operation without checking whether the caller was an administrator.

The vulnerable flow allowed a normal user request to reach `DVSA-ADMIN-UPDATE-ORDERS`, which updates the order status in DynamoDB.

Main causes:

- Missing admin authorization check
- Administrative action exposed through a public API path
- Backend trusted the request without verifying user privileges

## Environment

- Application: DVSA
- Region: `us-east-1`
- API endpoint: `https://d0xsecb8a2.execute-api.us-east-1.amazonaws.com/dvsa/order`
- Components: API Gateway, Lambda, DynamoDB
- Tools: Browser DevTools, Python script, Terminal, AWS Console

## Reproduction Steps

1. Logged in using a normal user account.
2. Captured the user Authorization token from Browser DevTools.
3. Used the order API endpoint.
4. Sent a crafted request using the administrative action `admin-update-orders`.
5. Attempted to update the target order status to `paid`.

Payload used:

```json
{
  "action": "admin-update-orders",
  "orderId": "de2c6970-56fc-4b61-8cc5-ef2faf5f4060",
  "status": "paid"
}
```

## Evidence

The API returned a successful response:

```json
{
  "status": "ok",
  "msg": "order updated"
}
```

DynamoDB confirmed that the order status changed from `delivered` to `paid`.

This proves that a normal authenticated user was able to perform an administrative order update without proper authorization.

All evidence screenshots are stored in the `evidence/` folder.

## Fix Strategy

The fix is to enforce role-based access control before allowing any administrative order update.

Only admin users should be allowed to invoke `admin-update-orders`. If the caller is not an administrator, the backend must reject the request before reaching the privileged Lambda function.

## Code Change

An admin authorization check was added before invoking `DVSA-ADMIN-UPDATE-ORDERS`.

Example secure logic:

```javascript
case "admin-update-orders":
    if (!isAdmin) {
        return callback(null, response(403, {
            status: "err",
            msg: "Unauthorized"
        }));
    }

    // Admin-only update logic continues here
    break;
```
## Verification After Fix

After applying the fix, the same request was repeated using a normal user token.

Expected result after fix: `{"status":"err","msg":"Unauthorized"}`

This confirms that normal users can no longer access the administrative update path.

Post-fix verification screenshots are stored in the `evidence/` folder.

## Security Analysis

| Item | Description |
|---|---|
| Vulnerability | Broken Access Control |
| Intended Rule | Only administrators should update order payment status |
| Exploit Behavior | Normal user changed order status to `paid` |
| Root Cause | Missing admin authorization check |
| Fix | Added admin validation before privileged update |
| Post-Fix Result | Normal user receives `Unauthorized` |

## Lessons Learned

Authentication alone is not enough. The backend must also verify authorization before performing sensitive actions.

Administrative operations should never be reachable by normal users through public API paths. Role-based access control must be enforced on the server side, especially for sensitive actions such as payment status updates.
