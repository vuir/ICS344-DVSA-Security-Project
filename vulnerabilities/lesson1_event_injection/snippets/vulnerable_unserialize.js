// Vulnerable input parsing logic in DVSA-ORDER-MANAGER.
// Problem: user-controlled input is passed directly into node-serialize.

const serialize = require('node-serialize');

var req = serialize.unserialize(event.body);
var headers = serialize.unserialize(event.headers);
