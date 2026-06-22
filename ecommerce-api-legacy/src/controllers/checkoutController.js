const CourseModel = require('../models/Course');
const EnrollmentService = require('../services/EnrollmentService');

async function checkout(req, res, next) {
    try {
        // REFACTORED: nomes descritivos no lugar de u, e, p, cid, cc (AP-12)
        const { usr: userName, eml: email, pwd: password, c_id: courseId, card: cardNumber } = req.body;

        if (!userName || !email || !courseId || !cardNumber) {
            return res.status(400).json({ erro: 'Campos obrigatórios: usr, eml, c_id, card' });
        }

        // REFACTORED: validação de entrada adicionada (AP-09)
        if (!email.includes('@')) {
            return res.status(400).json({ erro: 'Email inválido' });
        }
        if (!Number.isInteger(Number(courseId)) || Number(courseId) <= 0) {
            return res.status(400).json({ erro: 'c_id deve ser um inteiro positivo' });
        }
        if (String(cardNumber).length < 4) {
            return res.status(400).json({ erro: 'Número de cartão inválido' });
        }

        const course = await CourseModel.findActiveById(courseId);
        if (!course) return res.status(404).json({ erro: 'Curso não encontrado' });

        const result = await EnrollmentService.checkout({
            userName, email, password, courseId, cardNumber, course
        });

        res.status(200).json({ msg: 'Sucesso', enrollment_id: result.enrollmentId });
    } catch (err) {
        if (err.status) return res.status(err.status).json({ erro: err.message });
        next(err);
    }
}

module.exports = { checkout };
