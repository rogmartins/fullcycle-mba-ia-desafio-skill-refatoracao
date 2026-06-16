// REFACTORED: course database access extracted from AppManager God Class
class CourseModel {
    constructor(db) {
        this.db = db;
    }

    findActiveById(id) {
        return new Promise((resolve, reject) => {
            this.db.get("SELECT * FROM courses WHERE id = ? AND active = 1", [id], (err, row) => {
                if (err) reject(err);
                else resolve(row);
            });
        });
    }
}

module.exports = CourseModel;
