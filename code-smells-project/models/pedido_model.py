# REFACTORED: [CRITICAL/MEDIUM] Persistência de pedidos parametrizada, sem N+1 e sem duplicação.
from database import get_db
from constants import DESCONTO_FAIXAS, STATUS_PADRAO


def criar(usuario_id, total, linhas):
    """Persiste o pedido e seus itens. `linhas` = lista de (produto_id, quantidade, preco)."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, ?, ?)",
        (usuario_id, STATUS_PADRAO, total),
    )
    pedido_id = cursor.lastrowid

    for produto_id, quantidade, preco in linhas:
        cursor.execute(
            "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) "
            "VALUES (?, ?, ?, ?)",
            (pedido_id, produto_id, quantidade, preco),
        )
        cursor.execute(
            "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
            (quantidade, produto_id),
        )

    db.commit()
    return pedido_id


def get_pedidos(usuario_id=None):
    # REFACTORED: [MEDIUM] Função única para listar (antes get_pedidos_usuario/get_todos_pedidos duplicados).
    cursor = get_db().cursor()
    if usuario_id is None:
        cursor.execute("SELECT * FROM pedidos")
    else:
        cursor.execute("SELECT * FROM pedidos WHERE usuario_id = ?", (usuario_id,))
    pedidos_rows = cursor.fetchall()
    if not pedidos_rows:
        return []

    pedidos = {}
    ordem = []
    for row in pedidos_rows:
        pedidos[row["id"]] = {
            "id": row["id"],
            "usuario_id": row["usuario_id"],
            "status": row["status"],
            "total": row["total"],
            "criado_em": row["criado_em"],
            "itens": [],
        }
        ordem.append(row["id"])

    # REFACTORED: [MEDIUM] Itens carregados em uma única query com JOIN (antes N+1 em models.py:187/219).
    placeholders = ",".join("?" for _ in ordem)
    cursor.execute(
        "SELECT ip.pedido_id, ip.produto_id, ip.quantidade, ip.preco_unitario, "
        "       COALESCE(p.nome, 'Desconhecido') AS produto_nome "
        "FROM itens_pedido ip "
        "LEFT JOIN produtos p ON p.id = ip.produto_id "
        "WHERE ip.pedido_id IN (" + placeholders + ")",
        ordem,
    )
    for item in cursor.fetchall():
        pedidos[item["pedido_id"]]["itens"].append({
            "produto_id": item["produto_id"],
            "produto_nome": item["produto_nome"],
            "quantidade": item["quantidade"],
            "preco_unitario": item["preco_unitario"],
        })

    return [pedidos[pid] for pid in ordem]


def atualizar_status(pedido_id, novo_status):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("UPDATE pedidos SET status = ? WHERE id = ?", (novo_status, pedido_id))
    db.commit()
    return True


def relatorio_vendas():
    cursor = get_db().cursor()

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

    # REFACTORED: [LOW] Faixas de desconto via constante (antes números mágicos em models.py:257).
    desconto = 0
    for limiar, taxa in DESCONTO_FAIXAS:
        if faturamento > limiar:
            desconto = faturamento * taxa
            break

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
