from database import get_db

# REFACTORED: Model de Produto com queries parametrizadas (corrige SQL Injection)


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


class Produto:
    @staticmethod
    def listar():
        cursor = get_db().cursor()
        cursor.execute("SELECT * FROM produtos")
        return [_serialize(r) for r in cursor.fetchall()]

    @staticmethod
    def por_id(id):
        cursor = get_db().cursor()
        cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))
        row = cursor.fetchone()
        return _serialize(row) if row else None

    @staticmethod
    def criar(nome, descricao, preco, estoque, categoria):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) "
            "VALUES (?, ?, ?, ?, ?)",
            (nome, descricao, preco, estoque, categoria),
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def atualizar(id, nome, descricao, preco, estoque, categoria):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, "
            "estoque = ?, categoria = ? WHERE id = ?",
            (nome, descricao, preco, estoque, categoria, id),
        )
        db.commit()
        return True

    @staticmethod
    def deletar(id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM produtos WHERE id = ?", (id,))
        db.commit()
        return True

    @staticmethod
    def buscar(termo, categoria=None, preco_min=None, preco_max=None):
        # REFACTORED: WHERE dinâmico parametrizado (corrige SQL Injection no filtro)
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
        cursor.execute(query, tuple(params))
        return [_serialize(r) for r in cursor.fetchall()]
