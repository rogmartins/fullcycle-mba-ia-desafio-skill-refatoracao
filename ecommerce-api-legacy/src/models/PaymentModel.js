// REFACTORED: payment database access extracted from AppManager God Class
class PaymentModel {
    constructor(db) {
        this.db = db;
    }

    create(enrollmentId, amount, status) {
        return new Promise((resolve, reject) => {
            this.db.run("INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)", [enrollmentId, amount, status], function (err) {
                if (err) reject(err);
                else resolve(this.lastID);
            });
        });
    }

    deleteByEnrollmentId(enrollmentId) {
        return new Promise((resolve, reject) => {
            this.db.run("DELETE FROM payments WHERE enrollment_id = ?", [enrollmentId], (err) => {
                if (err) reject(err);
                else resolve();
            });
        });
    }
}

module.exports = PaymentModel;
