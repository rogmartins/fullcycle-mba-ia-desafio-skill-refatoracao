// REFACTORED: user management logic extracted from AppManager God Class route handler
class UserController {
    constructor(userModel, enrollmentModel, paymentModel) {
        this.userModel = userModel;
        this.enrollmentModel = enrollmentModel;
        this.paymentModel = paymentModel;
    }

    async deleteUser(req, res) {
        const userId = req.params.id;

        if (!Number.isInteger(Number(userId)) || Number(userId) <= 0) {
            return res.status(400).send("ID de usuário inválido");
        }

        try {
            // REFACTORED: cascade delete — payments → enrollments → user, preventing orphaned records
            const enrollments = await this.enrollmentModel.findByUserId(userId);
            for (const enrollment of enrollments) {
                await this.paymentModel.deleteByEnrollmentId(enrollment.id);
            }
            await this.enrollmentModel.deleteByUserId(userId);
            await this.userModel.deleteById(userId);

            return res.send("Usuário e dados associados deletados com sucesso.");
        } catch (err) {
            console.error(err);
            return res.status(500).send("Erro interno");
        }
    }
}

module.exports = UserController;
