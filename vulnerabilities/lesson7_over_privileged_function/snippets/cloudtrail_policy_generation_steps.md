# CloudTrail Policy Generation Steps

1. Open **CloudTrail → Trails**.
2. Create or enable a trail named `dvsa-policygen-trail`.
3. Enable management events.
4. Trigger a real DVSA order so `DVSA-SEND-RECEIPT-EMAIL` runs.
5. Confirm the function invocation in CloudWatch logs.
6. Open **IAM → Roles → serverlessrepo-OWASP-DVSA-SendReceiptFunctionRole-VciesI84W3Jt**.
7. Select **Generate policy based on CloudTrail events**.
8. Use the last 1 day, region `us-east-1`, and the `dvsa-policygen-trail` trail.
9. Review the generated actions and compare them against the broad policies attached to the role.

Purpose: prove that the function's real observed usage is much smaller than the permissions originally granted.
