# IAM Policy Simulator Test Cases

## Before Fix - Expected Over-Permissive Results

### S3 unrelated bucket test

Service: Amazon S3  
Actions: `GetObject`, `PutObject`, `DeleteObject`  
Resource:

```text
arn:aws:s3:::some-random-bucket-not-dvsa/some-key.txt
```

Expected vulnerable result: allowed.

### DynamoDB unrelated table test

Service: Amazon DynamoDB  
Actions: `Scan`, `GetItem`, `PutItem`, `DeleteItem`, `UpdateItem`  
Resource:

```text
arn:aws:dynamodb:us-east-1:716563790099:table/some-unrelated-table
```

Expected vulnerable result: allowed.

## After Fix - Expected Least-Privilege Results

- Random S3 bucket access should be denied.
- Receipt bucket `GetObject` and `PutObject` should be allowed.
- Receipt bucket `DeleteObject` should be denied.
- Random DynamoDB table access should be denied.
- `DVSA-ORDERS-DB` should allow only required actions such as `GetItem` and `UpdateItem`.
- SES should allow only `SendEmail` and `SendRawEmail`.
