// REFACTORED: [HIGH] Controller fino para usuários.
const userService = require('../services/userService');
const logger = require('../utils/logger');

async function remove(req, res) {
    try {
        await userService.deleteUser(req.params.id);
        // REFACTORED: [MEDIUM] Sem registros órfãos — matrículas e pagamentos removidos junto.
        return res.send('Usuário, matrículas e pagamentos removidos.');
    } catch (err) {
        logger.error('Erro ao deletar usuário:', err.message);
        return res.status(500).send('Erro ao deletar usuário');
    }
}

module.exports = { remove };
