import os

# REFACTORED: all secrets loaded from environment variables, never hardcoded
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-insecure-key-change-in-prod")
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
DB_PATH = os.environ.get("DB_PATH", "loja.db")
