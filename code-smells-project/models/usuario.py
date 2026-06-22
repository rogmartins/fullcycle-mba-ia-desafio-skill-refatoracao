from werkzeug.security import check_password_hash, generate_password_hash

from database import get_db

# REFACTORED: Model de Usuario com queries parametrizadas, hash de senha e
# serialização sem o campo senha (corrige SQL Injection, senha em texto puro e
# exposição de senha na API)


def _serialize_public(row):
    # REFACTORED: nunca expõe o campo senha
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
        "criado_em": row["criado_em"],
    }


class Usuario:
    @staticmethod
    def listar():
        cursor = get_db().cursor()
        cursor.execute("SELECT * FROM usuarios")
        return [_serialize_public(r) for r in cursor.fetchall()]

    @staticmethod
    def por_id(id):
        cursor = get_db().cursor()
        cursor.execute("SELECT * FROM usuarios WHERE id = ?", (id,))
        row = cursor.fetchone()
        return _serialize_public(row) if row else None

    @staticmethod
    def criar(nome, email, senha, tipo="cliente"):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
            (nome, email, generate_password_hash(senha), tipo),
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def autenticar(email, senha):
        # REFACTORED: query parametrizada + verificação de hash
        # (corrige SQL Injection na autenticação e comparação de senha em texto puro)
        cursor = get_db().cursor()
        cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        row = cursor.fetchone()
        if row and check_password_hash(row["senha"], senha):
            return {
                "id": row["id"],
                "nome": row["nome"],
                "email": row["email"],
                "tipo": row["tipo"],
            }
        return None
