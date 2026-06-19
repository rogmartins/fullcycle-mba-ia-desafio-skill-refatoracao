// REFACTORED: [CRITICAL] Configuração via variáveis de ambiente, sem segredos no código (antes utils.js:1).
const config = {
    port: process.env.PORT || 3000,
    dbUser: process.env.DB_USER || 'app',
    dbPass: process.env.DB_PASS || '',
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || '',
    smtpUser: process.env.SMTP_USER || '',
};

// REFACTORED: [LOW] Constantes nomeadas (antes números/strings mágicos).
const APPROVED_CARD_PREFIX = '4';
const PAYMENT_STATUS = { PAID: 'PAID', DENIED: 'DENIED' };

module.exports = { config, APPROVED_CARD_PREFIX, PAYMENT_STATUS };
