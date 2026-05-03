import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def parse_is_admin(event):
    """Safely parse the isAdmin field from a Lambda event."""
    is_admin_value = event.get("isAdmin", "false")

    if isinstance(is_admin_value, bool):
        return is_admin_value

    if isinstance(is_admin_value, str):
        value = is_admin_value.strip().lower()
        if value in ["true", "false"]:
            return json.loads(value)

    raise ValueError("Invalid isAdmin value")


def validate_order_id(event):
    """Reject missing, null, or non-string orderId values before DynamoDB access."""
    order_id = event.get("orderId")

    if not isinstance(order_id, str) or not order_id.strip():
        raise ValueError("Invalid orderId")

    return order_id


def safe_error_response(message="Invalid request"):
    """Return a generic client-safe error response."""
    return {
        "status": "err",
        "msg": message
    }
