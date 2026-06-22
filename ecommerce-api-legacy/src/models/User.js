// REFACTORED: model extraído de AppManager.js — encapsula queries de usuário (AP-05)
const { dbRun, dbGet, dbAll } = require('../database');
const { hashPassword } = require('../utils/crypto');

async function findByEmail(email) {
    return dbGet('SELECT id, name, email FROM users WHERE email = ?', [email]);
}

async function create(name, email, password) {
    const hashedPass = hashPassword(password);  // REFACTORED: hash correto no lugar de badCrypto (AP-01)
    const result = await dbRun('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)', [name, email, hashedPass]);
    return result.lastID;
}

async function deleteWithCascade(id) {
    // REFACTORED: deleção em cascata garante integridade referencial (AP-04)
    const enrollments = await dbAll('SELECT id FROM enrollments WHERE user_id = ?', [id]);
    for (const enr of enrollments) {
        await dbRun('DELETE FROM payments WHERE enrollment_id = ?', [enr.id]);
    }
    await dbRun('DELETE FROM enrollments WHERE user_id = ?', [id]);
    await dbRun('DELETE FROM users WHERE id = ?', [id]);
}

module.exports = { findByEmail, create, deleteWithCascade };
