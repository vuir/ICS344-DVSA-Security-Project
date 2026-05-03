// Safer input parsing logic.
// JSON.parse treats the request body as data only and does not reconstruct executable functions.

var req = JSON.parse(event.body);
var headers = event.headers;
