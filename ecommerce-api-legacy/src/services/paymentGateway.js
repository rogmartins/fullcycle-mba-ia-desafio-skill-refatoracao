// REFACTORED: [HIGH] Gateway de pagamento isolado (antes lógica inline no handler).
// REFACTORED: [CRITICAL] Não loga número de cartão nem a chave (antes AppManager.js:45).
const { APPROVED_CARD_PREFIX, PAYMENT_STATUS } = require('../config');
const logger = require('../utils/logger');

function maskCard(card) {
    const digits = String(card);
    return '**** **** **** ' + digits.slice(-4);
}

function authorize(card) {
    logger.info(`Processando pagamento do cartão ${maskCard(card)}`);
    return String(card).startsWith(APPROVED_CARD_PREFIX)
        ? PAYMENT_STATUS.PAID
        : PAYMENT_STATUS.DENIED;
}

module.exports = { authorize, maskCard };
