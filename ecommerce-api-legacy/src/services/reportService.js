// REFACTORED: [MEDIUM] Relatório financeiro sem N+1 (antes loops aninhados de queries em AppManager.js:89).
const db = require('../models/db');
const { PAYMENT_STATUS } = require('../config');

async function financialReport() {
    const courses = await db.all("SELECT * FROM courses ORDER BY id", []);

    // Uma única consulta carrega matrículas + aluno + pagamento (antes 1 + N*M queries).
    const linhas = await db.all(
        "SELECT e.id AS enrollment_id, e.course_id, u.name AS student, " +
        "       p.amount AS amount, p.status AS status " +
        "FROM enrollments e " +
        "LEFT JOIN users u ON u.id = e.user_id " +
        "LEFT JOIN payments p ON p.enrollment_id = e.id " +
        "ORDER BY e.id",
        [],
    );

    const porCurso = new Map();
    courses.forEach(c => porCurso.set(c.id, { course: c.title, revenue: 0, students: [] }));

    linhas.forEach(linha => {
        const data = porCurso.get(linha.course_id);
        if (!data) return;
        if (linha.status === PAYMENT_STATUS.PAID) {
            data.revenue += linha.amount;
        }
        data.students.push({
            student: linha.student || 'Unknown',
            paid: linha.amount != null ? linha.amount : 0,
        });
    });

    return courses.map(c => porCurso.get(c.id));
}

module.exports = { financialReport };
