// REFACTORED: [HIGH] Regra de negócio do checkout fora do handler (antes AppManager.js:28).
const db = require('../models/db');
const userModel = require('../models/userModel');
const courseModel = require('../models/courseModel');
const enrollmentModel = require('../models/enrollmentModel');
const paymentModel = require('../models/paymentModel');
const auditModel = require('../models/auditModel');
const paymentGateway = require('./paymentGateway');
const cache = require('../utils/cache');
const { PAYMENT_STATUS } = require('../config');
const { hashPassword } = require('../utils/crypto');
const AppError = require('./AppError');

async function checkout({ name, email, password, courseId, card }) {
    const course = await courseModel.findActiveById(courseId);
    if (!course) throw new AppError(404, 'Curso não encontrado');

    let user = await userModel.findByEmail(email);
    const userId = user
        ? user.id
        : await userModel.create(name, email, hashPassword(password || '123456'));

    const status = paymentGateway.authorize(card);
    if (status === PAYMENT_STATUS.DENIED) throw new AppError(400, 'Pagamento recusado');

    // REFACTORED: [HIGH] Matrícula + pagamento + auditoria em transação atômica (antes callbacks aninhados sem transação).
    await db.run('BEGIN');
    try {
        const enrollmentId = await enrollmentModel.create(userId, courseId);
        await paymentModel.create(enrollmentId, course.price, status);
        await auditModel.create(`Checkout curso ${courseId} por ${userId}`);
        await db.run('COMMIT');

        cache.set(`last_checkout_${userId}`, course.title);
        return { msg: 'Sucesso', enrollment_id: enrollmentId };
    } catch (err) {
        await db.run('ROLLBACK');
        throw err;
    }
}

module.exports = { checkout };
