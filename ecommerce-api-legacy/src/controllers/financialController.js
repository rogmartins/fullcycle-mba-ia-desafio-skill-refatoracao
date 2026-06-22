const PaymentModel = require('../models/Payment');

async function financialReport(req, res, next) {
    try {
        // REFACTORED: delegado ao model que usa JOIN único no lugar de N+1 callbacks (AP-08)
        const report = await PaymentModel.financialReport();
        res.json(report);
    } catch (err) {
        next(err);
    }
}

module.exports = { financialReport };
