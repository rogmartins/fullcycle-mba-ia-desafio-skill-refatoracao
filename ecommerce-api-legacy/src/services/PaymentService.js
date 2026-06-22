// REFACTORED: lógica de aprovação de pagamento extraída de AppManager.js:43 (AP-04)
const { paymentGatewayKey, VISA_PREFIX } = require('../config');

function approve(cardNumber, amount) {
    // REFACTORED: não loga o número completo do cartão nem a chave do gateway (AP-01)
    const lastFour = cardNumber.slice(-4);
    console.log(`Processando cartão ****${lastFour} — gateway configurado`);
    return cardNumber.startsWith(VISA_PREFIX) ? 'PAID' : 'DENIED';  // REFACTORED: constante nomeada (AP-11)
}

module.exports = { approve };
