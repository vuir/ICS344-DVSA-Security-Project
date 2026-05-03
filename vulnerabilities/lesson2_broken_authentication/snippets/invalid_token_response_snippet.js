verifyCognitoJwt(jwt).then((claims) => {
    var user = claims.username || claims["cognito:username"] || claims.sub;

    if (!user) {
        return callback(null, resp(401, { status: "err", msg: "missing subject" }));
    }

    // Continue normal request processing only after signature verification succeeds.
}).catch((e) => {
    console.log("JWT verify failed:", e);
    return callback(null, resp(401, { status: "err", msg: "invalid token" }));
});
