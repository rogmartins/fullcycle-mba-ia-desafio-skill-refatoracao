// REFACTORED: [HIGH] Rotas separadas da definição da aplicação (antes setupRoutes na God Class).
const express = require('express');
const checkoutController = require('../controllers/checkoutController');
const reportController = require('../controllers/reportController');
const userController = require('../controllers/userController');

const router = express.Router();

router.post('/api/checkout', checkoutController.checkout);
router.get('/api/admin/financial-report', reportController.financialReport);
router.delete('/api/users/:id', userController.remove);

module.exports = router;
