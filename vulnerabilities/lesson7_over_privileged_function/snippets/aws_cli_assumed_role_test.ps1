# Lesson 7 - Controlled assumed-role impact verification
# Use only in the authorized DVSA lab environment.
# Replace placeholders with redacted/temporary values captured during the controlled test.
# Remove any temporary Lambda instrumentation immediately after collecting evidence.

$env:AWS_ACCESS_KEY_ID = "PASTE_TEMP_ACCESS_KEY_ID_HERE"
$env:AWS_SECRET_ACCESS_KEY = "PASTE_TEMP_SECRET_ACCESS_KEY_HERE"
$env:AWS_SESSION_TOKEN = "PASTE_TEMP_SESSION_TOKEN_HERE"
$env:AWS_DEFAULT_REGION = "us-east-1"

# Confirm the terminal is operating as the Lambda execution role.
aws sts get-caller-identity

# S3 receipt bucket access test.
aws s3 ls s3://dvsa-receipts-bucket-716563790099-us-east-1/ --region us-east-1
aws s3 ls s3://dvsa-receipts-bucket-716563790099-us-east-1/ --recursive --region us-east-1

# DynamoDB blast-radius test.
# This should be denied after least-privilege restrictions are applied.
aws dynamodb scan --table-name DVSA-ORDERS-DB --region us-east-1
