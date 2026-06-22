// REFACTORED: app.js é agora apenas ponto de entrada (AP-03 — God Class decomposta)
const express = require('express');
const { port } = require('./config');
const { initSchema } = require('./database');
const routes = require('./routes');

const app = express();
app.use(express.json());
app.use(routes);

// REFACTORED: eliminados globalCache e totalRevenue do escopo global (AP-07)

app.use((err, req, res, next) => {
    console.error(err.message);
    res.status(500).json({ erro: 'Erro interno do servidor' });
});

initSchema()
    .then(() => {
        app.listen(port, () => {
            console.log(`LMS rodando na porta ${port}...`);
        });
    })
    .catch(err => {
        console.error('Falha ao inicializar banco:', err);
        process.exit(1);
    });

module.exports = app;
