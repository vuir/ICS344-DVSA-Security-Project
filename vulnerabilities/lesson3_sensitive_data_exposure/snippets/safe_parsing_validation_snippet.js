// Safer input parsing pattern for DVSA-ORDER-MANAGER.
// JSON.parse treats input as data, not executable JavaScript.
let obj;

try {
    obj = JSON.parse(userInput);
} catch (error) {
    return callback(null, {
        statusCode: 400,
        headers: { "Access-Control-Allow-Origin": "*" },
        body: JSON.stringify({ status: "err", msg: "bad request" })
    });
}

if (typeof obj.action !== "string" || obj.action.includes("_$$ND_FUNC$$_")) {
    return callback(null, {
        statusCode: 400,
        headers: { "Access-Control-Allow-Origin": "*" },
        body: JSON.stringify({ status: "err", msg: "invalid input" })
    });
}
