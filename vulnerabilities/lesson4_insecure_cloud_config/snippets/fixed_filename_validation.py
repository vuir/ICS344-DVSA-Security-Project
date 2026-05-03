# Lesson 4 - Fixed filename validation
# This snippet extracts only the filename, validates it, and rejects malformed input safely.

order = key.split("/")[-1]

if not order.endswith(".raw") or "_" not in order:
    print("Invalid receipt file name format:", order)
    return {"status": "err", "msg": "invalid file name format"}

parts = order.replace(".raw", "").split("_", 1)

if len(parts) != 2 or not parts[0] or not parts[1]:
    print("Invalid receipt file name parts:", order)
    return {"status": "err", "msg": "invalid file name format"}

orderId = parts[0]
userId = parts[1]
