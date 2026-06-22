const sqlite3 = require('sqlite3').verbose();
const { hashPassword } = require('./utils/crypto');

const db = new sqlite3.Database(':memory:');

const dbRun = (sql, params = []) => new Promise((resolve, reject) => {
    db.run(sql, params, function(err) {
        if (err) reject(err);
        else resolve({ lastID: this.lastID, changes: this.changes });
    });
});

const dbGet = (sql, params = []) => new Promise((resolve, reject) => {
    db.get(sql, params, (err, row) => {
        if (err) reject(err);
        else resolve(row);
    });
});

const dbAll = (sql, params = []) => new Promise((resolve, reject) => {
    db.all(sql, params, (err, rows) => {
        if (err) reject(err);
        else resolve(rows);
    });
});

async function initSchema() {
    await dbRun('CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, pass TEXT)');
    await dbRun('CREATE TABLE courses (id INTEGER PRIMARY KEY, title TEXT, price REAL, active INTEGER)');
    await dbRun('CREATE TABLE enrollments (id INTEGER PRIMARY KEY, user_id INTEGER, course_id INTEGER)');
    await dbRun('CREATE TABLE payments (id INTEGER PRIMARY KEY, enrollment_id INTEGER, amount REAL, status TEXT)');
    await dbRun('CREATE TABLE audit_logs (id INTEGER PRIMARY KEY, action TEXT, created_at DATETIME)');

    await dbRun('INSERT INTO users (name, email, pass) VALUES (?, ?, ?)',
        ['Leonan', 'leonan@fullcycle.com.br', hashPassword('123')]);
    await dbRun('INSERT INTO courses (title, price, active) VALUES (?, ?, ?)', ['Clean Architecture', 997.00, 1]);
    await dbRun('INSERT INTO courses (title, price, active) VALUES (?, ?, ?)', ['Docker', 497.00, 1]);
    await dbRun('INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)', [1, 1]);
    await dbRun('INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)', [1, 997.00, 'PAID']);
}

module.exports = { dbRun, dbGet, dbAll, initSchema };
