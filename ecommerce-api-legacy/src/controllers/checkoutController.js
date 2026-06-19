// REFACTORED: [HIGH] Controller fino: valida, chama o serviço, responde.
const checkoutService = require('../services/checkoutService');
const logger = require('../utils/logger');
const AppError = require('../services/AppError');

const EMAIL_RE = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;

async function checkout(req, res) {
    // REFACTORED: [LOW] Nomes descritivos (antes u, e, p, cid, cc).
    const { usr: name, eml: email, pwd: password, c_id: courseId, card } = req.body;

    if (!name || !email || !courseId || !card) return res.status(400).send('Bad Request');
    // REFACTORED: [MEDIUM] Validação de formato de email.
    if (!EMAIL_RE.test(email)) return res.status(400).send('Email inválido');

    try {
        const result = await checkoutService.checkout({ name, email, password, courseId, card });
        return res.status(200).json(result);
    } catch (err) {
        if (err instanceof AppError) return res.status(err.status).send(err.message);
        logger.error('Erro no checkout:', err.message);
        return res.status(500).send('Erro DB');
    }
}

module.exports = { checkout };
