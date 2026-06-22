// REFACTORED: model extraído de AppManager.js — encapsula queries de pagamento e relatório (AP-05)
const { dbRun, dbAll } = require('../database');

async function create(enrollmentId, amount, status) {
    const result = await dbRun(
        'INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)',
        [enrollmentId, amount, status]
    );
    return result.lastID;
}

async function financialReport() {
    // REFACTORED: substitui N+1 callbacks por uma única query com JOIN (AP-08)
    const rows = await dbAll(`
        SELECT
            c.title        AS course,
            u.name         AS student,
            p.amount       AS paid,
            p.status       AS paymentStatus
        FROM courses c
        LEFT JOIN enrollments e ON e.course_id = c.id
        LEFT JOIN users u       ON u.id = e.user_id
        LEFT JOIN payments p    ON p.enrollment_id = e.id
        ORDER BY c.id
    `);

    const report = {};
    for (const row of rows) {
        if (!report[row.course]) {
            report[row.course] = { course: row.course, revenue: 0, students: [] };
        }
        if (row.student) {
            if (row.paymentStatus === 'PAID') report[row.course].revenue += row.paid;
            report[row.course].students.push({ student: row.student, paid: row.paid || 0 });
        }
    }
    return Object.values(report);
}

module.exports = { create, financialReport };
