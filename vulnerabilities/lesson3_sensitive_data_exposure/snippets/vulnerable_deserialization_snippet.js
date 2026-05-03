// Vulnerable pattern: user-controlled input is passed to node-serialize.
// Any payload using _$$ND_FUNC$$_ can be reconstructed as executable JavaScript.
const serialize = require('node-serialize');

let obj = serialize.unserialize(userInput);
