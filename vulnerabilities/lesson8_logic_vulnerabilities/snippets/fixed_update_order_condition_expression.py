# Fixed pattern in update_order.py
# The status check is enforced atomically at write time by DynamoDB.

update_expr = "SET #itemList = :itemList"

try:
    response = table.update_item(
        Key={
            "orderId": orderId,
            "userId": userId
        },
        UpdateExpression=update_expr,
        ExpressionAttributeNames={
            "#itemList": "itemList"
        },
        ExpressionAttributeValues={
            ":itemList": itemList,
            ":maxStatus": 110
        },
        ConditionExpression="orderStatus <= :maxStatus"
    )
except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
    return {
        "status": "err",
        "msg": "order already paid"
    }
