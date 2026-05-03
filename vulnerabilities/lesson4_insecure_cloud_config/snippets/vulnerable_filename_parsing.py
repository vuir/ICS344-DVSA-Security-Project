# Lesson 4 - Vulnerable filename parsing
# This snippet assumes a fixed S3 key structure and filename format.
# It can crash when the uploaded filename does not contain an underscore.

order = key.split("/")[3]
orderId = order.split("_")[0]
userId = order.split("_")[1].replace(".raw", "")
