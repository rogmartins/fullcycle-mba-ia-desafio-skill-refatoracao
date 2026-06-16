// REFACTORED: user database access extracted from AppManager God Class
class UserModel {
    constructor(db) {
        this.db = db;
    }

    findByEmail(email) {
        return new Promise((resolve, reject) => {
            this.db.get("SELECT id, name, email FROM users WHERE email = ?", [email], (err, row) => {
                if (err) reject(err);
                else resolve(row);
            });
        });
    }

    create(name, email, passwordHash) {
        return new Promise((resolve, reject) => {
            this.db.run("INSERT INTO users (name, email, pass) VALUES (?, ?, ?)", [name, email, passwordHash], function (err) {
                if (err) reject(err);
                else resolve(this.lastID);
            });
        });
    }

    deleteById(id) {
        return new Promise((resolve, reject) => {
            this.db.run("DELETE FROM users WHERE id = ?", [id], (err) => {
                if (err) reject(err);
                else resolve();
            });
        });
    }
}

module.exports = UserModel;
