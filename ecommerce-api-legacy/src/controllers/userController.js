const UserModel = require('../models/User');

async function deleteUser(req, res, next) {
    try {
        const id = Number(req.params.id);
        if (!Number.isInteger(id) || id <= 0) {
            return res.status(400).json({ erro: 'ID inválido' });
        }
        // REFACTORED: deleção em cascata garante integridade referencial (AP-04)
        await UserModel.deleteWithCascade(id);
        res.json({ msg: 'Usuário e registros associados removidos com sucesso' });
    } catch (err) {
        next(err);
    }
}

module.exports = { deleteUser };
