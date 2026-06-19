// REFACTORED: [HIGH] Camada Model para pagamentos.
const db = require('./db');

async function create(enrollmentId, amount, status) {
    const { lastID } = await db.run(
        "INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)",
        [enrollmentId, amount, status],
    );
    return lastID;
}

// REFACTORED: [MEDIUM] Remoção em cascata dos pagamentos das matrículas de um usuário.
function deleteByUserId(userId) {
    return db.run(
        "DELETE FROM payments WHERE enrollment_id IN (SELECT id FROM enrollments WHERE user_id = ?)",
        [userId],
    );
}

module.exports = { create, deleteByUserId };
