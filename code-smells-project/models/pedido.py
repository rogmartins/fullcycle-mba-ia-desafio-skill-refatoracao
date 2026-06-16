from database import get_db

_STATUS_VALIDOS = ["pendente", "aprovado", "enviado", "entregue", "cancelado"]


def criar_pedido(usuario_id, itens):
    db = get_db()
    cursor = db.cursor()

    total = 0
    itens_validados = []

    for item in itens:
        cursor.execute("SELECT * FROM produtos WHERE id = ?", (item["produto_id"],))  # REFACTORED: parametrized query prevents SQL Injection (SELECT)
        produto = cursor.fetchone()
        if produto is None:
            return {"erro": f"Produto {item['produto_id']} não encontrado"}
        if produto["estoque"] < item["quantidade"]:
            return {"erro": f"Estoque insuficiente para {produto['nome']}"}
        total += produto["preco"] * item["quantidade"]
        itens_validados.append((item, produto))

    cursor.execute(  # REFACTORED: parametrized query prevents SQL Injection (INSERT)
        "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, ?, ?)",
        (usuario_id, "pendente", total),
    )
    pedido_id = cursor.lastrowid

    for item, produto in itens_validados:
        cursor.execute(  # REFACTORED: parametrized query prevents SQL Injection (INSERT)
            "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
            (pedido_id, item["produto_id"], item["quantidade"], produto["preco"]),
        )
        cursor.execute(  # REFACTORED: parametrized query prevents SQL Injection (UPDATE)
            "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
            (item["quantidade"], item["produto_id"]),
        )

    db.commit()
    return {"pedido_id": pedido_id, "total": total}


def get_pedidos_usuario(usuario_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(  # REFACTORED: single JOIN eliminates N+1 pattern; parametrized prevents SQL Injection (SELECT)
        """SELECT p.id, p.usuario_id, p.status, p.total, p.criado_em,
                  ip.produto_id, ip.quantidade, ip.preco_unitario, pr.nome AS produto_nome
           FROM pedidos p
           LEFT JOIN itens_pedido ip ON ip.pedido_id = p.id
           LEFT JOIN produtos pr ON pr.id = ip.produto_id
           WHERE p.usuario_id = ?
           ORDER BY p.id""",
        (usuario_id,),
    )
    return _aggregate_pedidos(cursor.fetchall())


def get_todos_pedidos():
    db = get_db()
    cursor = db.cursor()
    cursor.execute(  # REFACTORED: single JOIN eliminates N+1 pattern (was 1+N+(N×M) queries)
        """SELECT p.id, p.usuario_id, p.status, p.total, p.criado_em,
                  ip.produto_id, ip.quantidade, ip.preco_unitario, pr.nome AS produto_nome
           FROM pedidos p
           LEFT JOIN itens_pedido ip ON ip.pedido_id = p.id
           LEFT JOIN produtos pr ON pr.id = ip.produto_id
           ORDER BY p.id"""
    )
    return _aggregate_pedidos(cursor.fetchall())


def atualizar_status_pedido(pedido_id, novo_status):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(  # REFACTORED: parametrized query prevents SQL Injection (UPDATE)
        "UPDATE pedidos SET status = ? WHERE id = ?",
        (novo_status, pedido_id),
    )
    db.commit()
    return True


def relatorio_dados_brutos():
    """Return raw aggregates only. Business rules are applied in services/relatorio_service.py."""
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT COUNT(*) FROM pedidos")
    total_pedidos = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(total) FROM pedidos")
    faturamento = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'pendente'")
    pendentes = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'aprovado'")
    aprovados = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status = 'cancelado'")
    cancelados = cursor.fetchone()[0]

    return {
        "total_pedidos": total_pedidos,
        "faturamento_bruto": round(faturamento, 2),
        "pedidos_pendentes": pendentes,
        "pedidos_aprovados": aprovados,
        "pedidos_cancelados": cancelados,
    }


def _aggregate_pedidos(rows):
    # REFACTORED: shared helper eliminates duplicated pedido-serialization logic
    pedidos = {}
    for row in rows:
        pid = row["id"]
        if pid not in pedidos:
            pedidos[pid] = {
                "id": pid,
                "usuario_id": row["usuario_id"],
                "status": row["status"],
                "total": row["total"],
                "criado_em": row["criado_em"],
                "itens": [],
            }
        if row["produto_id"] is not None:
            pedidos[pid]["itens"].append({
                "produto_id": row["produto_id"],
                "produto_nome": row["produto_nome"] or "Desconhecido",
                "quantidade": row["quantidade"],
                "preco_unitario": row["preco_unitario"],
            })
    return list(pedidos.values())
