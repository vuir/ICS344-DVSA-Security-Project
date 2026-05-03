# Lesson 9: Vulnerable Dependencies

> This lesson is demonstrated together with **Lesson 1: Event Injection** because both lessons use the same exploit, root cause, fix, and evidence.

---

## How to Use This Folder

1. Read this README to understand the dependency issue.
2. Open `../lesson1_event_injection/README.md` for the full reproduction steps and screenshots.
3. Use `snippets/dependency_audit_commands.md` to document the dependency cleanup process.
4. Use `snippets/package_json_before_after.md` to explain what changed in the package configuration.

---

## 1. Vulnerability Summary

This lesson demonstrates how a vulnerable third-party dependency can create a critical security issue in a serverless application.

The affected dependency is `node-serialize`, a Node.js package used by `DVSA-ORDER-MANAGER`. The package can deserialize JavaScript functions when it sees the `_$$ND_FUNC$$_` marker. When this behavior is applied to untrusted API input, the result is Remote Code Execution inside the Lambda runtime.

Lesson 1 shows the attack behavior. Lesson 9 explains the dependency weakness that made the attack possible.

---

## 2. Root Cause

The root cause is unsafe dependency use:

- The application used `node-serialize` for untrusted request data.
- The dependency can reconstruct executable JavaScript functions.
- The application did not need executable deserialization for normal JSON request handling.
- The vulnerable package was not removed or replaced before deployment.

A normal API request should be parsed as data. Instead, the dependency allowed user-controlled text to become executable code.

---

## 3. Environment

| Item | Value |
|---|---|
| Application | DVSA |
| AWS Region | `us-east-1` |
| Lambda Function | `DVSA-ORDER-MANAGER` |
| Vulnerable Package | `node-serialize` |
| Related Lesson | Lesson 1: Event Injection |
| Tools Used | AWS Lambda Console, Postman, CloudWatch, npm audit |

---

## 4. Prerequisites

Before reviewing this lesson:

1. Open the Lesson 1 folder.
2. Review the exploit payload and CloudWatch proof of execution.
3. Review the vulnerable code that uses `serialize.unserialize()`.
4. Review the fixed code that uses `JSON.parse()`.

---

## 5. Step-by-Step Reproduction

The full reproduction steps are documented in:

```text
../lesson1_event_injection/README.md
```

Summary:

1. Send a crafted payload containing `_$$ND_FUNC$$_` to the order API.
2. `node-serialize` deserializes the payload.
3. The embedded function executes inside Lambda.
4. CloudWatch logs confirm backend code execution.

---

## 6. Attack Result Summary Before Fix

| Result | Detail |
|---|---|
| Code execution | Confirmed in Lambda |
| Root dependency | `node-serialize` |
| Proof | CloudWatch showed `FILE READ SUCCESS` |
| Risk | Any AWS resource reachable by the Lambda role could be exposed |

---

## 7. Fix Strategy

The fix is to remove unsafe dependency behavior from the request path.

Required changes:

- Do not use `node-serialize` on user-controlled input.
- Replace deserialization with `JSON.parse()`.
- Validate request fields manually.
- Remove `node-serialize` from `package.json` if not needed.
- Run dependency checks such as `npm audit`.

---

## 8. Code / Config Changes

The main code change is documented in the Lesson 1 folder.

Before:

```javascript
const serialize = require('node-serialize');
var req = serialize.unserialize(event.body);
```

After:

```javascript
var req = JSON.parse(event.body);
```

Dependency cleanup commands are documented in:

```text
snippets/dependency_audit_commands.md
snippets/package_json_before_after.md
```

---

## 9. Verification After Fix

After replacing `node-serialize` with `JSON.parse()`, repeat the same payload used in Lesson 1.

Expected result:

- The payload is treated as a normal string.
- No embedded function executes.
- CloudWatch does not show `FILE READ SUCCESS`.
- Normal order requests continue to work.

---

## 10. Security Analysis

### Table 1 — Intended vs. Observed Behavior

| Vulnerability | Intended Rule(s) | Artifacts Used | Normal Behavior Evidence | Exploit Behavior Evidence |
|---|---|---|---|---|
| Vulnerable Dependencies | Dependencies must not execute user-controlled input. | Lambda code, package configuration, payload, CloudWatch logs | Safe JSON parsing treats input as data. | `node-serialize` executed a function embedded in user input. |

### Table 2 — Deviation Analysis and Fix

| Vulnerability | Why This Is a Deviation | Deviation Class | Fix Applied | Post-Fix Verification | Latency |
|---|---|---|---|---|---|
| Vulnerable Dependencies | A third-party package introduced executable deserialization into an API request path. | Accidental Misconfiguration / Unsafe Dependency Use | Removed unsafe deserialization and replaced it with `JSON.parse()`; audited dependency usage. | Same payload no longer executes in Lambda. | Not measured |

---

## 11. Lessons Learned

Security is not only about the code written by the developer. Third-party packages can introduce dangerous behavior, especially when they process user-controlled input.

The main lesson is that dependencies must be reviewed, minimized, and audited. A utility package should not be allowed to change data parsing into code execution.

---

## Repository Structure

```text
lesson9_vulnerable_dependencies/
│
├── README.md
└── snippets/
    ├── dependency_audit_commands.md
    └── package_json_before_after.md
```
