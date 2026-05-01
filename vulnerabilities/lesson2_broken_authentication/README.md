# Lesson 2: Broken Authentication

## Vulnerability Summary

This lesson demonstrates a Broken Authentication vulnerability caused by improper validation of JSON Web Tokens (JWT).

The backend trusted identity claims such as `username` and `sub` from the JWT payload without properly verifying the token signature. Because of this, an attacker could modify the JWT payload and make the system treat them as another user.

The impact is user impersonation and unauthorized access to another user’s private order data.

## Root Cause

The application decoded the JWT payload and trusted its contents without verifying whether the token was genuinely issued by the trusted identity provider.

Main causes:

- Missing JWT signature verification
- Trusting user-controlled JWT claims
- Using `username` and `sub` directly for authorization decisions
- Weak authentication validation in the backend

## Environment

- Application: DVSA
- Region: `us-east-1`
- API endpoint: `https://d0xsecb8a2.execute-api.us-east-1.amazonaws.com/dvsa/order`
- Component: `DVSA-ORDER-MANAGER`
- File: `order-manager.js`
- Tools: Browser DevTools, Terminal, curl, jq, Python

## Reproduction Steps

1. Created two normal users: User B and User C.
2. Both users logged in and placed at least one order.
3. Captured `TOKEN_B` and `TOKEN_C` from Browser DevTools.
4. Confirmed that User B’s original token only returned User B’s own orders.
5. Modified the JWT payload by replacing User B identity fields with User C identity fields.
6. Re-encoded the token and saved it as `FAKE_AS_C`.
7. Sent a request using the forged token.
8. The backend accepted the forged token and returned User C’s private order list.

## Evidence

Using User B’s original token, the API returned only User B’s orders.

After modifying the JWT payload and using the forged token, the API returned User C’s private order data.

Returned victim order example:

- `order-id`: `de2c6970-56fc-4b61-8cc5-ef2faf5f4060`
- `total`: `44`
- `status`: `delivered`

This proves that the backend trusted the modified JWT payload without properly verifying the token signature.

All evidence screenshots are stored in the `evidence/` folder.

## Fix Strategy

The fix is to verify the JWT signature before trusting any identity claims inside the token.

The backend should reject tampered, expired, or unverifiable tokens and should only use verified claims for authentication and authorization decisions.

Recommended fixes:

- Verify JWT signature using Cognito JWKS public keys
- Validate required claims such as `iss`, `exp`, `aud`, and `token_use`
- Reject modified or expired tokens
- Avoid trusting client-controlled JWT payload fields directly

## Code Change

JWT verification was added inside `order-manager.js`.

The secure flow verifies the token signature using Cognito public keys before trusting `username` or `sub`.

If verification fails, the backend returns:

`{"status":"err","msg":"invalid token"}`

This prevents forged tokens from being accepted.

## Verification After Fix

After applying the fix, the same forged JWT token was tested again.

Before the fix, the forged token returned User C’s private order list.

After the fix, the backend rejected the forged token and returned:

`{"status":"err","msg":"invalid token"}`

This confirms that JWT signature verification is enforced and tampered tokens are no longer accepted.

Post-fix verification screenshots are stored in the `evidence/` folder.

## Security Analysis

| Item | Description |
|---|---|
| Vulnerability | Broken Authentication |
| Intended Rule | Only valid and verified JWT tokens should determine user identity |
| Exploit Behavior | Forged token returned another user’s order data |
| Root Cause | Backend trusted JWT payload without verifying signature |
| Fix | Added JWT signature verification and claim validation |
| Post-Fix Result | Forged token returns `invalid token` |

## Lessons Learned

JWT payloads should never be trusted unless the token signature is cryptographically verified.

Authentication must be based on trusted server-side validation, not decoded client-controlled token contents. Proper JWT verification prevents token forgery, user impersonation, and unauthorized access to protected resources.