case "admin-update-orders":
    if (req["isAdmin"] !== "true") {
        return {
            statusCode: 403,
            headers: { "Access-Control-Allow-Origin": "*" },
            body: JSON.stringify({
                status: "err",
                msg: "Unauthorized"
            })
        };
    }

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
