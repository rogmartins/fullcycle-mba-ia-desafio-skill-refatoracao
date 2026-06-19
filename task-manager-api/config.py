# REFACTORED: [CRITICAL] Configuração via variáveis de ambiente, sem segredos no código.
import os
import secrets


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI", "sqlite:///tasks.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # REFACTORED: [CRITICAL] SECRET_KEY do ambiente (antes app.py:13 hardcoded).
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    # REFACTORED: [HIGH] DEBUG por ambiente, desligado por padrão (antes app.py:34 fixo).
    DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"

    # REFACTORED: [CRITICAL] Credenciais SMTP do ambiente (antes notification_service.py:9).
    SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
    SMTP_USER = os.environ.get("SMTP_USER", "")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
