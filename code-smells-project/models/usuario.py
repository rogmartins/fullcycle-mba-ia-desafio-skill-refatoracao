from database import get_db


def get_todos_usuarios():
    db = get_db()
    cursor = db.cursor()
    # REFACTORED: exclude senha column from listing response (AP-04)
    cursor.execute("SELECT id, nome, email, tipo, criado_em FROM usuarios")
    return [dict(row) for row in cursor.fetchall()]


def get_usuario_por_id(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, nome, email, tipo, criado_em FROM usuarios WHERE id=?", (id,))  # REFACTORED: parameterized (AP-02)
    row = cursor.fetchone()
    return dict(row) if row else None


def login_usuario(email, senha):
    db = get_db()
    cursor = db.cursor()
    # REFACTORED: parameterized query prevents authentication bypass via SQL injection (AP-02)
    cursor.execute(
        "SELECT * FROM usuarios WHERE email=? AND senha=?",
        (email, senha)
    )
    row = cursor.fetchone()
    if row:
        return {"id": row["id"], "nome": row["nome"], "email": row["email"], "tipo": row["tipo"]}
    return None


def criar_usuario(nome, email, senha, tipo="cliente"):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?,?,?,?)",  # REFACTORED: parameterized INSERT (AP-02)
        (nome, email, senha, tipo)
    )
    db.commit()
    return cursor.lastrowid
