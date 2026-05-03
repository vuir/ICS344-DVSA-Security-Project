# Run the DoS Test Script

Set the required environment variables first:

```bash
export DVSA_API_URL="https://<api-id>.execute-api.us-east-1.amazonaws.com/dvsa/order"
export DVSA_TOKEN="<paste_normal_user_token_here>"
export DVSA_ORDER_ID="<paste_order_id_here>"
export DVSA_THREAD_COUNT="200"
```

Install the dependency:

```bash
pip install -r requirements.txt
```

Run the script:

```bash
python dos_test.py
```
