import os

# REFACTORED: credenciais e configurações sensíveis movidas para variáveis de ambiente (AP-01)
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-only-change-in-production')
DATABASE_URI = os.environ.get('DATABASE_URI', 'sqlite:///tasks.db')
DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'

SMTP_HOST = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', '587'))
SMTP_USER = os.environ.get('SMTP_USER', '')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')
