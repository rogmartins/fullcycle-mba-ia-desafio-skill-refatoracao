# REFACTORED: [MEDIUM] Erro de serviço com status HTTP, traduzido pelas rotas.
class ServiceError(Exception):
    def __init__(self, status, message):
        super().__init__(message)
        self.status = status
        self.message = message
