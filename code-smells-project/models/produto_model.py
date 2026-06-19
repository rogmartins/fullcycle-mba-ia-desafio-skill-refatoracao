# REFACTORED: [CRITICAL] Todas as queries parametrizadas (antes SQL Injection em models.py).
from database import get_db

CAMPOS = ["id", "nome", "descricao", "preco", "estoque", "categoria", "ativo", "criado_em"]


def _to_dict(row):
    return {campo: row[campo] for campo in CAMPOS}


def get_todos():
    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM produtos")
    return [_to_dict(row) for row in cursor.fetchall()]


def get_por_id(id):
    cursor = get_db().cursor()
    # REFACTORED: [CRITICAL] SELECT parametrizado (antes models.py:28).
    cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))
    row = cursor.fetchone()
    return _to_dict(row) if row else None


def criar(nome, descricao, preco, estoque, categoria):
    db = get_db()
    cursor = db.cursor()
    # REFACTORED: [CRITICAL] INSERT parametrizado (antes models.py:48).
    cursor.execute(
        "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
        (nome, descricao, preco, estoque, categoria),
    )
    db.commit()
    return cursor.lastrowid


def atualizar(id, nome, descricao, preco, estoque, categoria):
    db = get_db()
    cursor = db.cursor()
    # REFACTORED: [CRITICAL] UPDATE parametrizado (antes models.py:58).
    cursor.execute(
        "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ? WHERE id = ?",
        (nome, descricao, preco, estoque, categoria, id),
    )
    db.commit()
    return True


def deletar(id):
    db = get_db()
    cursor = db.cursor()
    # REFACTORED: [CRITICAL] DELETE parametrizado (antes models.py:68).
    cursor.execute("DELETE FROM produtos WHERE id = ?", (id,))
    db.commit()
    return True


def buscar(termo, categoria=None, preco_min=None, preco_max=None):
    # REFACTORED: [CRITICAL] WHERE dinâmico com placeholders (antes models.py:289).
    query = "SELECT * FROM produtos WHERE 1=1"
    params = []
    if termo:
        query += " AND (nome LIKE ? OR descricao LIKE ?)"
        like = "%" + termo + "%"
        params.extend([like, like])
    if categoria:
        query += " AND categoria = ?"
        params.append(categoria)
    if preco_min:
        query += " AND preco >= ?"
        params.append(preco_min)
    if preco_max:
        query += " AND preco <= ?"
        params.append(preco_max)

    cursor = get_db().cursor()
    cursor.execute(query, params)
    return [_to_dict(row) for row in cursor.fetchall()]
