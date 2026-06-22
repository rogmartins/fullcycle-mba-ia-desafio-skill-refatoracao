// REFACTORED: fluxo de checkout extraído de AppManager.js:43-77 (AP-04)
const UserModel = require('../models/User');
const EnrollmentModel = require('../models/Enrollment');
const PaymentModel = require('../models/Payment');
const PaymentService = require('./PaymentService');
const { dbRun } = require('../database');

async function checkout({ userName, email, password, courseId, cardNumber, course }) {
    let user = await UserModel.findByEmail(email);
    let userId;

    if (!user) {
        userId = await UserModel.create(userName, email, password || '123456');
    } else {
        userId = user.id;
    }

    const status = PaymentService.approve(cardNumber, course.price);
    if (status === 'DENIED') {
        throw Object.assign(new Error('Pagamento recusado'), { status: 400 });
    }

    const enrollmentId = await EnrollmentModel.create(userId, courseId);
    await PaymentModel.create(enrollmentId, course.price, status);
    await dbRun(
        "INSERT INTO audit_logs (action, created_at) VALUES (?, datetime('now'))",
        [`Checkout curso ${courseId} por ${userId}`]
    );

    return { enrollmentId, userId };
}

module.exports = { checkout };
