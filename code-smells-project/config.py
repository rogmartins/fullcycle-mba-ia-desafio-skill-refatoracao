import os

# REFACTORED: credentials moved from hardcoded values to environment variables (AP-01)
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-in-production")
DATABASE_PATH = os.environ.get("DATABASE_PATH", "loja.db")
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"

# REFACTORED: extracted magic strings from controllers.py:52 (AP-11)
CATEGORIAS_VALIDAS = ["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]

# REFACTORED: extracted magic numbers from models.py:257 (AP-11)
DESCONTO_LIMITE_ALTO = 10000
DESCONTO_LIMITE_MEDIO = 5000
DESCONTO_LIMITE_BAIXO = 1000
DESCONTO_PERCENTUAL_ALTO = 0.10
DESCONTO_PERCENTUAL_MEDIO = 0.05
DESCONTO_PERCENTUAL_BAIXO = 0.02
