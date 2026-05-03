# API Gateway Throttling Settings

Location:

```text
API Gateway → APIs → DVSA API → Stages → Stage → Edit
```

Change the default stage throttling values:

| Setting | Before | After |
|---|---:|---:|
| Rate | 10000 | 5 |
| Burst | 5000 | 10 |
```
Save changes and redeploy the stage if required.
```
