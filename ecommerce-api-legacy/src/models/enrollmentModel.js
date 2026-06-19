// REFACTORED: [HIGH] Camada Model para matrículas.
const db = require('./db');

async function create(userId, courseId) {
    const { lastID } = await db.run(
        "INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)",
        [userId, courseId],
    );
    return lastID;
}

function deleteByUserId(userId) {
    return db.run("DELETE FROM enrollments WHERE user_id = ?", [userId]);
}

module.exports = { create, deleteByUserId };
