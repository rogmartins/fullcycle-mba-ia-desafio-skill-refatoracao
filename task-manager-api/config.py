import os
from dotenv import load_dotenv

load_dotenv()

# REFACTORED: credenciais e configurações movidas para variáveis de ambiente
DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///tasks.db')
SECRET_KEY = os.environ.get('SECRET_KEY', 'change-me-in-production')

EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USER = os.environ.get('EMAIL_USER', '')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', '')

JWT_EXPIRATION_HOURS = int(os.environ.get('JWT_EXPIRATION_HOURS', 24))
