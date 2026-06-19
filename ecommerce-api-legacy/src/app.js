// REFACTORED: [CRITICAL] app.js enxuto — sem God Class; apenas monta a aplicação.
const express = require('express');
const { config } = require('./config');
const db = require('./models/db');
const routes = require('./routes');
const logger = require('./utils/logger');

async function start() {
    await db.init();

    const app = express();
    app.use(express.json());
    app.use(routes);

    app.listen(config.port, () => {
        logger.info(`LMS rodando na porta ${config.port}...`);
    });
}

start().catch((err) => {
    logger.error('Falha ao iniciar a aplicação:', err);
    process.exit(1);
});
