# REFACTORED: [CRITICAL] Queries parametrizadas + senha nunca exposta.
from werkzeug.security import check_password_hash, generate_password_hash

from database import get_db

# REFACTORED: [CRITICAL] Campos públicos não incluem "senha" (antes exposta em GET /usuarios).
CAMPOS_PUBLICOS = ["id", "nome", "email", "tipo", "criado_em"]


def _to_dict(row):
    return {campo: row[campo] for campo in CAMPOS_PUBLICOS}


def get_todos():
    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM usuarios")
    return [_to_dict(row) for row in cursor.fetchall()]


def get_por_id(id):
    cursor = get_db().cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id = ?", (id,))
    row = cursor.fetchone()
    return _to_dict(row) if row else None


def email_existe(email):
    cursor = get_db().cursor()
    cursor.execute("SELECT 1 FROM usuarios WHERE email = ?", (email,))
    return cursor.fetchone() is not None


def criar(nome, email, senha, tipo="cliente"):
    db = get_db()
    cursor = db.cursor()
    # REFACTORED: [CRITICAL] Senha gravada com hash (antes texto puro em models.py:126).
    cursor.execute(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
        (nome, email, generate_password_hash(senha), tipo),
    )
    db.commit()
    return cursor.lastrowid


def autenticar(email, senha):
    cursor = get_db().cursor()
    # REFACTORED: [CRITICAL] Consulta de login parametrizada + verificação de hash
    # (antes models.py:109 concatenava email/senha, permitindo bypass de login).
    cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
    row = cursor.fetchone()
    if row and check_password_hash(row["senha"], senha):
        return {"id": row["id"], "nome": row["nome"], "email": row["email"], "tipo": row["tipo"]}
    return None
