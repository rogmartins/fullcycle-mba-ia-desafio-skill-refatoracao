// REFACTORED: enrollment database access extracted from AppManager God Class
class EnrollmentModel {
    constructor(db) {
        this.db = db;
    }

    create(userId, courseId) {
        return new Promise((resolve, reject) => {
            this.db.run("INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)", [userId, courseId], function (err) {
                if (err) reject(err);
                else resolve(this.lastID);
            });
        });
    }

    findByUserId(userId) {
        return new Promise((resolve, reject) => {
            this.db.all("SELECT id FROM enrollments WHERE user_id = ?", [userId], (err, rows) => {
                if (err) reject(err);
                else resolve(rows);
            });
        });
    }

    deleteByUserId(userId) {
        return new Promise((resolve, reject) => {
            this.db.run("DELETE FROM enrollments WHERE user_id = ?", [userId], (err) => {
                if (err) reject(err);
                else resolve();
            });
        });
    }

    // REFACTORED: single JOIN query replaces N+1 nested callbacks in financial-report handler
    getFinancialReport() {
        return new Promise((resolve, reject) => {
            const sql = `
                SELECT c.id AS course_id, c.title AS course_title,
                       u.name AS student_name,
                       p.amount AS payment_amount, p.status AS payment_status
                FROM courses c
                LEFT JOIN enrollments e ON e.course_id = c.id
                LEFT JOIN users u ON u.id = e.user_id
                LEFT JOIN payments p ON p.enrollment_id = e.id
            `;
            this.db.all(sql, [], (err, rows) => {
                if (err) reject(err);
                else resolve(rows);
            });
        });
    }
}

module.exports = EnrollmentModel;
