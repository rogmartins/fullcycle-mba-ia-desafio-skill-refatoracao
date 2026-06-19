// REFACTORED: [HIGH] Camada Model para logs de auditoria.
const db = require('./db');

function create(action) {
    return db.run(
        "INSERT INTO audit_logs (action, created_at) VALUES (?, datetime('now'))",
        [action],
    );
}

module.exports = { create };
