// REFACTORED: audit log database access extracted from AppManager God Class
class AuditLogModel {
    constructor(db) {
        this.db = db;
    }

    log(action) {
        return new Promise((resolve, reject) => {
            this.db.run("INSERT INTO audit_logs (action, created_at) VALUES (?, datetime('now'))", [action], (err) => {
                if (err) reject(err);
                else resolve();
            });
        });
    }
}

module.exports = AuditLogModel;
