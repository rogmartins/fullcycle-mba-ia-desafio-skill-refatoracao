// REFACTORED: [MEDIUM] Erros de negócio com status HTTP associado.
class AppError extends Error {
    constructor(status, message) {
        super(message);
        this.status = status;
    }
}

module.exports = AppError;
