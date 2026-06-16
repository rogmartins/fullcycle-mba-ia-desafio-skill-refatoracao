// REFACTORED: entry point simplified — DB init and routing delegated to dedicated modules
const express = require('express');
const { createDb, initDb } = require('./database/db');
const createRouter = require('./routes/index');
const env = require('./config/env');

const app = express();
app.use(express.json());

const db = createDb();

initDb(db).then((db) => {
    app.use(createRouter(db));
    app.listen(env.port, () => {
        console.log(`ecommerce-api rodando na porta ${env.port}...`);
    });
}).catch((err) => {
    console.error('Falha ao inicializar banco de dados:', err);
    process.exit(1);
});
