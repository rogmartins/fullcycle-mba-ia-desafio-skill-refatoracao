// REFACTORED: route registration extracted from AppManager God Class
const { Router } = require('express');

const UserModel = require('../models/UserModel');
const CourseModel = require('../models/CourseModel');
const EnrollmentModel = require('../models/EnrollmentModel');
const PaymentModel = require('../models/PaymentModel');
const AuditLogModel = require('../models/AuditLogModel');

const CheckoutController = require('../controllers/CheckoutController');
const FinancialController = require('../controllers/FinancialController');
const UserController = require('../controllers/UserController');

function createRouter(db) {
    // REFACTORED: dependencies injected, not hardcoded inside route handlers
    const userModel = new UserModel(db);
    const courseModel = new CourseModel(db);
    const enrollmentModel = new EnrollmentModel(db);
    const paymentModel = new PaymentModel(db);
    const auditLogModel = new AuditLogModel(db);

    const checkoutController = new CheckoutController(userModel, courseModel, enrollmentModel, paymentModel, auditLogModel);
    const financialController = new FinancialController(enrollmentModel);
    const userController = new UserController(userModel, enrollmentModel, paymentModel);

    const router = Router();

    router.post('/api/checkout', (req, res) => checkoutController.checkout(req, res));
    router.get('/api/admin/financial-report', (req, res) => financialController.financialReport(req, res));
    router.delete('/api/users/:id', (req, res) => userController.deleteUser(req, res));

    return router;
}

module.exports = createRouter;
