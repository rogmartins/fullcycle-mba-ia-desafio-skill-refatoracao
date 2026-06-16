// REFACTORED: database instantiation and initialization extracted from AppManager God Class
const sqlite3 = require('sqlite3').verbose();
const bcrypt = require('bcryptjs');
const env = require('../config/env');

function createDb() {
    return new sqlite3.Database(env.dbPath);
}

function initDb(db) {
    return new Promise((resolve, reject) => {
        db.serialize(async () => {
            db.run("PRAGMA foreign_keys = ON");
            db.run("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, pass TEXT)");
            db.run("CREATE TABLE courses (id INTEGER PRIMARY KEY, title TEXT, price REAL, active INTEGER)");
            db.run("CREATE TABLE enrollments (id INTEGER PRIMARY KEY, user_id INTEGER, course_id INTEGER, FOREIGN KEY(user_id) REFERENCES users(id), FOREIGN KEY(course_id) REFERENCES courses(id))");
            db.run("CREATE TABLE payments (id INTEGER PRIMARY KEY, enrollment_id INTEGER, amount REAL, status TEXT, FOREIGN KEY(enrollment_id) REFERENCES enrollments(id))");
            db.run("CREATE TABLE audit_logs (id INTEGER PRIMARY KEY, action TEXT, created_at DATETIME)");

            // REFACTORED: seed password hashed with bcrypt instead of plaintext
            const seedPasswordHash = bcrypt.hashSync('123', 12);
            db.run("INSERT INTO users (name, email, pass) VALUES (?, ?, ?)", ['Leonan', 'leonan@fullcycle.com.br', seedPasswordHash]);
            db.run("INSERT INTO courses (title, price, active) VALUES (?, ?, ?), (?, ?, ?)",
                ['Clean Architecture', 997.00, 1, 'Docker', 497.00, 1]);
            db.run("INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)", [1, 1]);
            db.run("INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)", [1, 997.00, 'PAID'], (err) => {
                if (err) return reject(err);
                resolve(db);
            });
        });
    });
}

module.exports = { createDb, initDb };
