# Lesson 4 Payload Files

These files are harmless sample upload files used to reproduce and verify the S3/Lambda behavior.

| File | Purpose |
|---|---|
| `test.raw` | Malformed filename used before the fix to trigger the Lambda parsing failure. |
| `12345_abcde.raw` | Valid filename pattern used before the fix to show normal processing. |
| `badtest.raw` | Malformed filename used after the fix to verify safe rejection. |
| `6789_abcde.raw` | Valid filename pattern used after the fix to verify normal functionality still works. |

The content of the files is not important for this lesson. The filename format is what triggers the behavior.
