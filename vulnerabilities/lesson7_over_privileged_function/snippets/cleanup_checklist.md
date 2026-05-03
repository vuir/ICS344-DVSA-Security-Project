# Lesson 7 Cleanup Checklist

- [ ] Remove temporary `print(dict(os.environ))` instrumentation from Lambda.
- [ ] Redeploy `DVSA-SEND-RECEIPT-EMAIL` after removing instrumentation.
- [ ] Redact temporary credential values in all screenshots.
- [ ] Delete or expire any temporary credentials from local shell history where possible.
- [ ] Confirm `AmazonSESFullAccess` is detached.
- [ ] Confirm invalid `SendReceiptFunctionRolePolicy3` is deleted.
- [ ] Confirm final IAM role has only the scoped policies needed for the receipt workflow.
- [ ] Re-run IAM Policy Simulator post-fix tests.
- [ ] Place a normal order to confirm the workflow still works.
