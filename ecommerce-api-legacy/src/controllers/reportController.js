// REFACTORED: [HIGH] Controller fino para o relatório financeiro.
const reportService = require('../services/reportService');
const logger = require('../utils/logger');

async function financialReport(req, res) {
    try {
        const report = await reportService.financialReport();
        return res.json(report);
    } catch (err) {
        logger.error('Erro no relatório:', err.message);
        return res.status(500).send('Erro DB');
    }
}

module.exports = { financialReport };
