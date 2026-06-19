# REFACTORED: [LOW] Removidos imports e funções não utilizados (código morto).
def format_date(date_obj):
    return str(date_obj) if date_obj else None


def calculate_percentage(part, total):
    if total == 0:
        return 0
    return round((part / total) * 100, 2)
