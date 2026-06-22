import os

# REFACTORED: configuração centralizada e lida de variáveis de ambiente
# (corrige SECRET_KEY hardcoded e DEBUG fixo em produção)


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
    DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"
    DB_PATH = os.environ.get("DB_PATH", "loja.db")
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", "5000"))
