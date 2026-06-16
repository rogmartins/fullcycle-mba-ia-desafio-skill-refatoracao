from database import get_db
from werkzeug.security import generate_password_hash, check_password_hash


def get_todos_usuarios():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM usuarios")
    return [_serialize(row) for row in cursor.fetchall()]


def get_usuario_por_id(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE id = ?", (id,))  # REFACTORED: parametrized query prevents SQL Injection (SELECT)
    row = cursor.fetchone()
    return _serialize(row) if row else None


def criar_usuario(nome, email, senha, tipo="cliente"):
    db = get_db()
    cursor = db.cursor()
    senha_hash = generate_password_hash(senha)  # REFACTORED: password hashed before storage
    cursor.execute(  # REFACTORED: parametrized query prevents SQL Injection (INSERT)
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
        (nome, email, senha_hash, tipo),
    )
    db.commit()
    return cursor.lastrowid


def login_usuario(email, senha):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(  # REFACTORED: parametrized query prevents SQL Injection (Authentication Bypass)
        "SELECT * FROM usuarios WHERE email = ?",
        (email,),
    )
    row = cursor.fetchone()
    if row and check_password_hash(row["senha"], senha):  # REFACTORED: hash comparison prevents plaintext credential exposure
        return _serialize(row)
    return None


def _serialize(row):
    # REFACTORED: password field excluded — never returned in API responses
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
        "criado_em": row["criado_em"],
    }
