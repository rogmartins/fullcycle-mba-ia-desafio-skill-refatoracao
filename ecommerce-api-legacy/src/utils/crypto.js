// REFACTORED: [CRITICAL] Hash de senha com sal usando crypto nativo (antes badCrypto quebrado em utils.js:17).
const crypto = require('crypto');

function hashPassword(plain) {
    const salt = crypto.randomBytes(16).toString('hex');
    const derived = crypto.scryptSync(String(plain), salt, 32).toString('hex');
    return `${salt}:${derived}`;
}

function verifyPassword(plain, stored) {
    const [salt, derived] = String(stored).split(':');
    if (!salt || !derived) return false;
    const candidate = crypto.scryptSync(String(plain), salt, 32).toString('hex');
    return crypto.timingSafeEqual(Buffer.from(derived, 'hex'), Buffer.from(candidate, 'hex'));
}

module.exports = { hashPassword, verifyPassword };
