from database import get_db

# REFACTORED: named constant replaces magic string list in controller
CATEGORIAS_VALIDAS = ["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]


def get_todos_produtos():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM produtos")
    return [_serialize(row) for row in cursor.fetchall()]


def get_produto_por_id(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))  # REFACTORED: parametrized query prevents SQL Injection (SELECT)
    row = cursor.fetchone()
    return _serialize(row) if row else None


def criar_produto(nome, descricao, preco, estoque, categoria):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(  # REFACTORED: parametrized query prevents SQL Injection (INSERT)
        "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
        (nome, descricao, preco, estoque, categoria),
    )
    db.commit()
    return cursor.lastrowid


def atualizar_produto(id, nome, descricao, preco, estoque, categoria):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(  # REFACTORED: parametrized query prevents SQL Injection (UPDATE)
        "UPDATE produtos SET nome=?, descricao=?, preco=?, estoque=?, categoria=? WHERE id=?",
        (nome, descricao, preco, estoque, categoria, id),
    )
    db.commit()
    return True


def deletar_produto(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM produtos WHERE id = ?", (id,))  # REFACTORED: parametrized query prevents SQL Injection (DELETE)
    db.commit()
    return True


def buscar_produtos(termo, categoria=None, preco_min=None, preco_max=None):
    db = get_db()
    cursor = db.cursor()

    # REFACTORED: dynamic WHERE builder uses parameterized placeholders — prevents SQL Injection
    conditions = ["1=1"]
    params = []

    if termo:
        conditions.append("(nome LIKE ? OR descricao LIKE ?)")
        params.extend([f"%{termo}%", f"%{termo}%"])
    if categoria:
        conditions.append("categoria = ?")
        params.append(categoria)
    if preco_min is not None:
        conditions.append("preco >= ?")
        params.append(preco_min)
    if preco_max is not None:
        conditions.append("preco <= ?")
        params.append(preco_max)

    cursor.execute("SELECT * FROM produtos WHERE " + " AND ".join(conditions), params)
    return [_serialize(row) for row in cursor.fetchall()]


def _serialize(row):
    return {
        "id": row["id"],
        "nome": row["nome"],
        "descricao": row["descricao"],
        "preco": row["preco"],
        "estoque": row["estoque"],
        "categoria": row["categoria"],
        "ativo": row["ativo"],
        "criado_em": row["criado_em"],
    }
