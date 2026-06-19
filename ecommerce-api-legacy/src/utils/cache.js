// REFACTORED: [HIGH] Cache encapsulado em módulo (antes globalCache mutável global em utils.js:9).
const logger = require('./logger');

const store = {};

function set(key, value) {
    logger.info(`Salvando no cache: ${key}`);
    store[key] = value;
}

function get(key) {
    return store[key];
}

module.exports = { set, get };
