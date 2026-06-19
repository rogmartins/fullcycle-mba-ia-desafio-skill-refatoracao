# REFACTORED: [CRITICAL] Configuração centralizada, sem segredos no código-fonte.
import os
import secrets


class Config:
    """Configuração da aplicação lida de variáveis de ambiente.

    Nenhum segredo fica embutido no código. Quando SECRET_KEY não é
    fornecida, uma chave aleatória é gerada em tempo de execução (apropriado
    para desenvolvimento, nunca para produção com sessões persistentes).
    """

    # REFACTORED: [CRITICAL] SECRET_KEY vem do ambiente (antes hardcoded em app.py:7)
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)

    # REFACTORED: [HIGH] DEBUG controlado por ambiente, desligado por padrão (antes app.py:8 = True)
    DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"

    DB_PATH = os.environ.get("DB_PATH", "loja.db")
    AMBIENTE = os.environ.get("APP_ENV", "desenvolvimento")
    VERSAO = "1.0.0"

    # REFACTORED: [HIGH] Token para proteger rotas administrativas destrutivas
    ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN")
