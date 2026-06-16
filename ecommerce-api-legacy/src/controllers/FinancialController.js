// REFACTORED: financial report logic extracted from AppManager God Class route handler
const { PAYMENT_STATUS } = require('../config/constants');

class FinancialController {
    constructor(enrollmentModel) {
        this.enrollmentModel = enrollmentModel;
    }

    async financialReport(req, res) {
        try {
            // REFACTORED: single JOIN query replaces N+1 nested callbacks
            const rows = await this.enrollmentModel.getFinancialReport();

            const reportMap = {};
            for (const row of rows) {
                if (!reportMap[row.course_id]) {
                    reportMap[row.course_id] = { course: row.course_title, revenue: 0, students: [] };
                }
                if (row.student_name) {
                    reportMap[row.course_id].students.push({
                        student: row.student_name,
                        paid: row.payment_amount || 0,
                    });
                    if (row.payment_status === PAYMENT_STATUS.PAID) {
                        reportMap[row.course_id].revenue += row.payment_amount;
                    }
                }
            }

            return res.json(Object.values(reportMap));
        } catch (err) {
            console.error(err);
            return res.status(500).send("Erro interno");
        }
    }
}

module.exports = FinancialController;
