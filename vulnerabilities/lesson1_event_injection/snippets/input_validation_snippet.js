// Additional validation to reject suspicious action values before application logic continues.
// This check is defense-in-depth. The main fix is removing node-serialize from untrusted input parsing.

function validateOrderRequest(req) {
    if (!req || typeof req !== 'object') {
        throw new Error('Invalid request body');
    }

    if (typeof req.action !== 'string') {
        throw new Error('Invalid action field');
    }

    if (req.action.includes('_$$ND_FUNC$$_')) {
        throw new Error('Suspicious serialized function payload rejected');
    }

    return true;
}

validateOrderRequest(req);
