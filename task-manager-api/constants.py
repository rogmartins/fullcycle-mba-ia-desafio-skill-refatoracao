# REFACTORED: [LOW/MEDIUM] Constantes nomeadas centralizadas (antes valores mágicos repetidos nas rotas).
VALID_STATUSES = ["pending", "in_progress", "done", "cancelled"]
VALID_ROLES = ["user", "admin", "manager"]
TERMINAL_STATUSES = ["done", "cancelled"]

MIN_TITLE_LENGTH = 3
MAX_TITLE_LENGTH = 200
MIN_PASSWORD_LENGTH = 4
MIN_PRIORITY = 1
MAX_PRIORITY = 5
DEFAULT_PRIORITY = 3
DEFAULT_COLOR = "#000000"

EMAIL_REGEX = r"^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$"
