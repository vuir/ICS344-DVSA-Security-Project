# AWS WAF Rate-Based Rule

Create or update a Web ACL and associate it with the API Gateway stage.

Suggested rule:

```text
Rule name: BlockHighRateIPs
Rule type: Rate-based rule
Rate limit: 100 requests per 5 minutes per IP
Action: Block
Resource: API Gateway Stage
```

After applying the rule, repeat the same high-concurrency test. High-rate requests should return:

```json
{"message":"Forbidden"}
```
