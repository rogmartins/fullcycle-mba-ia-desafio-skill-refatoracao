// REFACTORED: [MEDIUM] Exclusão de usuário em cascata e transacional (antes deixava órfãos).
const db = require('../models/db');
const userModel = require('../models/userModel');
const enrollmentModel = require('../models/enrollmentModel');
const paymentModel = require('../models/paymentModel');

async function deleteUser(id) {
    await db.run('BEGIN');
    try {
        await paymentModel.deleteByUserId(id);
        await enrollmentModel.deleteByUserId(id);
        await userModel.deleteById(id);
        await db.run('COMMIT');
    } catch (err) {
        await db.run('ROLLBACK');
        throw err;
    }
}

module.exports = { deleteUser };
