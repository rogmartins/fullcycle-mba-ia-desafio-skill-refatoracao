// REFACTORED: checkout business logic extracted from AppManager God Class route handler
const bcrypt = require('bcryptjs');
const { PAYMENT_STATUS, VISA_BIN_PREFIX } = require('../config/constants');
const env = require('../config/env');

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

class CheckoutController {
    constructor(userModel, courseModel, enrollmentModel, paymentModel, auditLogModel) {
        this.userModel = userModel;
        this.courseModel = courseModel;
        this.enrollmentModel = enrollmentModel;
        this.paymentModel = paymentModel;
        this.auditLogModel = auditLogModel;
    }

    async checkout(req, res) {
        // REFACTORED: meaningful variable names instead of single-letter aliases
        const { usr: userName, eml: email, pwd: password, c_id: courseId, card: cardNumber } = req.body;

        // REFACTORED: explicit input validation replacing bare truthy checks
        if (!userName || !email || !courseId || !cardNumber) {
            return res.status(400).send("Bad Request");
        }
        if (!EMAIL_REGEX.test(email)) {
            return res.status(400).send("E-mail inválido");
        }
        if (!Number.isInteger(Number(courseId)) || Number(courseId) <= 0) {
            return res.status(400).send("ID de curso inválido");
        }
        if (String(cardNumber).length < 13) {
            return res.status(400).send("Número de cartão inválido");
        }
        // REFACTORED: explicit password requirement — no silent default of "123456"
        if (!password || password.length < 6) {
            return res.status(400).send("Senha obrigatória (mínimo 6 caracteres)");
        }

        try {
            const course = await this.courseModel.findActiveById(courseId);
            if (!course) return res.status(404).send("Curso não encontrado");

            let user = await this.userModel.findByEmail(email);
            let userId;

            if (!user) {
                // REFACTORED: bcryptjs replaces badCrypto reversible encoding
                const passwordHash = await bcrypt.hash(password, 12);
                userId = await this.userModel.create(userName, email, passwordHash);
            } else {
                userId = user.id;
            }

            // REFACTORED: payment status from named constants instead of inline magic strings
            console.log(`Processando cartão na chave ${env.paymentGatewayKey}`);
            const paymentStatus = cardNumber.startsWith(VISA_BIN_PREFIX)
                ? PAYMENT_STATUS.PAID
                : PAYMENT_STATUS.DENIED;

            if (paymentStatus === PAYMENT_STATUS.DENIED) {
                return res.status(400).send("Pagamento recusado");
            }

            const enrollmentId = await this.enrollmentModel.create(userId, courseId);
            await this.paymentModel.create(enrollmentId, course.price, paymentStatus);
            await this.auditLogModel.log(`Checkout curso ${courseId} por ${userId}`);

            return res.status(200).json({ msg: "Sucesso", enrollment_id: enrollmentId });
        } catch (err) {
            console.error(err);
            return res.status(500).send("Erro interno");
        }
    }
}

module.exports = CheckoutController;
