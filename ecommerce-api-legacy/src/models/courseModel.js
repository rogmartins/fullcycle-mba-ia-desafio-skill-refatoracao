// REFACTORED: [HIGH] Camada Model para cursos.
const db = require('./db');

function findActiveById(id) {
    return db.get("SELECT * FROM courses WHERE id = ? AND active = 1", [id]);
}

function all() {
    return db.all("SELECT * FROM courses", []);
}

module.exports = { findActiveById, all };
