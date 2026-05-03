# Lesson 4 - S3 Block Public Access Fix

Apply this configuration change in the AWS Console:

1. Open **S3**.
2. Select the receipt bucket used by the DVSA application.
3. Open the **Permissions** tab.
4. In **Block public access (bucket settings)**, choose **Edit**.
5. Enable **Block all public access**.
6. Save changes and confirm the setting.

Expected result: the bucket displays **Block all public access: On**.
