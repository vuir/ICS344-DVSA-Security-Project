import json

"""
ICS344 DVSA Security Project
Lesson 10 - Unhandled Exceptions

This script documents the malformed payload used to trigger an unhandled
exception in the DVSA-ORDER-GET Lambda function.
"""

malformed_payload = {
    "orderId": None,
    "isAdmin": True
}

print("=" * 60)
print("Lesson 10 - Unhandled Exceptions Test Payload")
print("=" * 60)
print(json.dumps(malformed_payload, indent=4))
print("-" * 60)
print("Expected vulnerable behavior:")
print("AttributeError: 'bool' object has no attribute 'lower'")
print("-" * 60)
print("Expected fixed behavior:")
print("The function should safely validate input and return a controlled error.")
print("=" * 60)
