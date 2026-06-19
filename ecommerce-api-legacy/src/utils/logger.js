// REFACTORED: [LOW] Logger simples com níveis (antes console.log solto, inclusive de dados sensíveis).
const logger = {
    info: (...args) => console.log('[INFO]', ...args),
    warn: (...args) => console.warn('[WARN]', ...args),
    error: (...args) => console.error('[ERROR]', ...args),
};

module.exports = logger;
