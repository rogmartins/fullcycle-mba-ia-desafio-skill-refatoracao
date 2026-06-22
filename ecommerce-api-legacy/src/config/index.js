// REFACTORED: credenciais movidas de utils.js para variáveis de ambiente (AP-01)
module.exports = {
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || '',
    port: process.env.PORT || 3000,
    VISA_PREFIX: '4',  // REFACTORED: string mágica extraída para constante nomeada (AP-11)
};
