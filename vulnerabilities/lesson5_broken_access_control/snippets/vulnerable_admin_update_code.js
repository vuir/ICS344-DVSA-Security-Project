case "admin-update-orders":
    payload = {
        "action": "update",
        "order-id": req["order-id"],
        "userId": req["userId"] || req["user"] || "anonymous",
        "status": req["status"] || "paid",
        "itemList": req["itemList"] || [],
        "address": req["address"] || {},
        "token": req["token"] || "lesson5",
        "total": req["total"] || 0
    };
    functionName = "DVSA-ADMIN-UPDATE-ORDERS";
    break;
