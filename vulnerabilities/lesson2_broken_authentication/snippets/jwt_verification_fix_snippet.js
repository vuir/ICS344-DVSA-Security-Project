const https = require("https");
const jose = require("node-jose");

let _jwksCache = { keystore: null, fetchedAt: 0 };

function fetchJson(url) {
    return new Promise((resolve, reject) => {
        https.get(url, (res) => {
            let data = "";
            res.on("data", (chunk) => data += chunk);
            res.on("end", () => {
                if (res.statusCode < 200 || res.statusCode >= 300) {
                    return reject(new Error(`HTTP ${res.statusCode}: ${data.slice(0, 200)}`));
                }
                try {
                    resolve(JSON.parse(data));
                } catch (e) {
                    reject(e);
                }
            });
        }).on("error", reject);
    });
}

async function getCognitoKeystore() {
    if (_jwksCache.keystore && Date.now() - _jwksCache.fetchedAt < 60 * 60 * 1000) {
        return _jwksCache.keystore;
    }

    const issuer = `https://cognito-idp.${process.env.AWS_REGION}.amazonaws.com/${process.env.userpoolid}`;
    const jwks = await fetchJson(`${issuer}/.well-known/jwks.json`);
    const keystore = await jose.JWK.asKeyStore(jwks);

    _jwksCache = { keystore, fetchedAt: Date.now() };
    return keystore;
}

async function verifyCognitoJwt(jwt) {
    const keystore = await getCognitoKeystore();
    const result = await jose.JWS.createVerify(keystore).verify(jwt);
    const claims = JSON.parse(result.payload.toString());

    const expectedIssuer = `https://cognito-idp.${process.env.AWS_REGION}.amazonaws.com/${process.env.userpoolid}`;

    if (claims.iss !== expectedIssuer) {
        throw new Error("invalid issuer");
    }

    if (claims.exp * 1000 < Date.now()) {
        throw new Error("token expired");
    }

    if (claims.token_use !== "access") {
        throw new Error("invalid token_use");
    }

    return claims;
}
