from database import get_db
from config import (
    DESCONTO_LIMITE_ALTO, DESCONTO_LIMITE_MEDIO, DESCONTO_LIMITE_BAIXO,
    DESCONTO_PERCENTUAL_ALTO, DESCONTO_PERCENTUAL_MEDIO, DESCONTO_PERCENTUAL_BAIXO,
)


def _montar_pedidos_com_itens(db, pedidos_rows):
    # REFACTORED: eager loading with JOIN replaces N+1 query pattern (AP-08)
    if not pedidos_rows:
        return []
    pedido_ids = [row["id"] for row in pedidos_rows]
    placeholders = ",".join(["?"] * len(pedido_ids))
    cursor = db.cursor()
    cursor.execute(
        f"SELECT ip.*, p.nome AS produto_nome "
        f"FROM itens_pedido ip "
        f"JOIN produtos p ON p.id = ip.produto_id "
        f"WHERE ip.pedido_id IN ({placeholders})",
        pedido_ids
    )
    itens_por_pedido = {}
    for item in cursor.fetchall():
        pid = item["pedido_id"]
        itens_por_pedido.setdefault(pid, []).append({
            "produto_id": item["produto_id"],
            "produto_nome": item["produto_nome"],
            "quantidade": item["quantidade"],
            "preco_unitario": item["preco_unitario"],
        })
    result = []
    for row in pedidos_rows:
        pedido = dict(row)
        pedido["itens"] = itens_por_pedido.get(row["id"], [])
        result.append(pedido)
    return result


def get_pedidos_usuario(usuario_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM pedidos WHERE usuario_id=?", (usuario_id,))  # REFACTORED: parameterized (AP-02)
    rows = cursor.fetchall()
    return _montar_pedidos_com_itens(db, rows)


def get_todos_pedidos():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM pedidos")
    rows = cursor.fetchall()
    return _montar_pedidos_com_itens(db, rows)


def criar_pedido(usuario_id, itens):
    db = get_db()
    cursor = db.cursor()
    total = 0
    for item in itens:
        cursor.execute("SELECT * FROM produtos WHERE id=?", (item["produto_id"],))  # REFACTORED: parameterized (AP-02)
        produto = cursor.fetchone()
        if produto is None:
            return {"erro": f"Produto {item['produto_id']} não encontrado"}
        if produto["estoque"] < item["quantidade"]:
            return {"erro": f"Estoque insuficiente para {produto['nome']}"}
        total += produto["preco"] * item["quantidade"]
    cursor.execute(
        "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",  # REFACTORED: parameterized (AP-02)
        (usuario_id, total)
    )
    pedido_id = cursor.lastrowid
    for item in itens:
        cursor.execute("SELECT preco FROM produtos WHERE id=?", (item["produto_id"],))  # REFACTORED: parameterized (AP-02)
        produto = cursor.fetchone()
        cursor.execute(
            "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?,?,?,?)",  # REFACTORED: parameterized (AP-02)
            (pedido_id, item["produto_id"], item["quantidade"], produto["preco"])
        )
        cursor.execute(
            "UPDATE produtos SET estoque = estoque - ? WHERE id=?",  # REFACTORED: parameterized (AP-02)
            (item["quantidade"], item["produto_id"])
        )
    db.commit()
    return {"pedido_id": pedido_id, "total": total}


def atualizar_status_pedido(pedido_id, novo_status):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE pedidos SET status=? WHERE id=?",  # REFACTORED: parameterized (AP-02)
        (novo_status, pedido_id)
    )
    db.commit()
    return True


def relatorio_vendas():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM pedidos")
    total_pedidos = cursor.fetchone()[0]
    cursor.execute("SELECT SUM(total) FROM pedidos")
    faturamento = cursor.fetchone()[0] or 0
    cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status='pendente'")
    pendentes = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status='aprovado'")
    aprovados = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM pedidos WHERE status='cancelado'")
    cancelados = cursor.fetchone()[0]

    # REFACTORED: use named constants instead of magic numbers (AP-11)
    desconto = 0
    if faturamento > DESCONTO_LIMITE_ALTO:
        desconto = faturamento * DESCONTO_PERCENTUAL_ALTO
    elif faturamento > DESCONTO_LIMITE_MEDIO:
        desconto = faturamento * DESCONTO_PERCENTUAL_MEDIO
    elif faturamento > DESCONTO_LIMITE_BAIXO:
        desconto = faturamento * DESCONTO_PERCENTUAL_BAIXO

    return {
        "total_pedidos": total_pedidos,
        "faturamento_bruto": round(faturamento, 2),
        "desconto_aplicavel": round(desconto, 2),
        "faturamento_liquido": round(faturamento - desconto, 2),
        "pedidos_pendentes": pendentes,
        "pedidos_aprovados": aprovados,
        "pedidos_cancelados": cancelados,
        "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0,
    }
