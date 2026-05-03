# Lesson 9: Vulnerable Dependencies

> **This lesson is demonstrated together with Lesson 1: Event Injection.**
> Full reproduction steps, evidence, code changes, and analysis are in:
> **[Lesson 1 README](../lesson1_event_injection/README.md)**

---

## Why These Two Lessons Are Combined

Lesson 1 and Lesson 9 share the exact same exploit, the same root cause, and the same fix. Separating them would mean duplicating all evidence and steps. Instead:

- **Lesson 1** covers the attack — what happens when event injection succeeds
- **Lesson 9** covers the reason it is possible — the `node-serialize` package is the vulnerable dependency that enables the attack

---

## The Vulnerable Dependency

The affected library is **`node-serialize`**, a Node.js package that serializes and deserializes JavaScript objects, including functions.

When an object containing the `_$$ND_FUNC$$_` marker is passed to `unserialize()`, the library reconstructs the function and executes it immediately if the string ends with `()`. This behavior is by design in the library — which is exactly why it must never be used on untrusted input.

**Known vulnerability:** CVE-2017-5941

---

## Impact

- Remote Code Execution (RCE) inside the Lambda runtime
- File system access (`/tmp`) from attacker-controlled code
- Potential access to any AWS resource the Lambda IAM role can reach

---

## Fix Summary

| Change | Detail |
|---|---|
| Remove | `node-serialize` from `package.json` and `node_modules` |
| Replace | `serialize.unserialize(event.body)` with `JSON.parse(event.body)` |
| Add | Input validation to reject non-string or suspicious `action` values |
| Audit | Run `npm audit` regularly to catch known-vulnerable packages early |

---

## Key Lesson

Security is not only about your own code — **your dependencies can break your system too.**

`node-serialize` looked like a utility library. It introduced a direct path to full backend code execution. One `npm audit` or a quick review of the package's known issues would have flagged it before deployment.

Always:
- Review third-party libraries before adding them
- Run `npm audit` (or equivalent) as part of your deployment pipeline
- Replace any library that processes executable content from user input
- Treat all user input as untrusted data, regardless of the library used to parse it

---

## Repository Structure

```
lesson9_vulnerable_dependencies/
│
└── README.md    <- This file (links to Lesson 1 for full details)
```