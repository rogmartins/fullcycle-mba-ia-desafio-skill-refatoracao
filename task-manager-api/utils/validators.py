# REFACTORED: [MEDIUM] Validação de email centralizada (antes regex inline duplicada).
import re

from constants import EMAIL_REGEX

_EMAIL_RE = re.compile(EMAIL_REGEX)


def is_valid_email(email):
    return bool(email and _EMAIL_RE.match(email))
