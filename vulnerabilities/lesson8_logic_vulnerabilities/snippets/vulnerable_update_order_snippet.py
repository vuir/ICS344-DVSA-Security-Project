# Vulnerable pattern in update_order.py
# The status check and write are separate operations, creating a TOCTOU race window.

response = table.get_item(
    Key={
        "orderId": orderId,
        "userId": userId
    },
    AttributesToGet=["orderStatus"]
)

if response["Item"]["orderStatus"] > 110:
    return {"status": "err", "msg": "order already paid"}

update_expr = "SET {} = :itemList".format("itemList")
response = table.update_item(
    Key={"orderId": orderId, "userId": userId},
    UpdateExpression=update_expr,
    ExpressionAttributeValues={
        ":itemList": itemList
    }
)
