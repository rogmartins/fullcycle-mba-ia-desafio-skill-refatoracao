from constants import FAIXAS_DESCONTO
from database import get_db

# REFACTORED: Model de Pedido com queries parametrizadas e leitura sem N+1
# (uma query para pedidos + uma query para itens via JOIN)


def _carregar_pedidos(where_clause="", params=()):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM pedidos " + where_clause + " ORDER BY id", params)
    pedidos_rows = cursor.fetchall()
    if not pedidos_rows:
        return []

    pedido_ids = [r["id"] for r in pedidos_rows]
    placeholders = ",".join("?" * len(pedido_ids))
    cursor.execute(
        "SELECT ip.pedido_id, ip.produto_id, ip.quantidade, ip.preco_unitario, "
        "p.nome AS produto_nome FROM itens_pedido ip "
        "LEFT JOIN produtos p ON p.id = ip.produto_id "
        "WHERE ip.pedido_id IN (" + placeholders + ")",
        tuple(pedido_ids),
    )
    itens_por_pedido = {}
    for it in cursor.fetchall():
        itens_por_pedido.setdefault(it["pedido_id"], []).append(
            {
                "produto_id": it["produto_id"],
                "produto_nome": it["produto_nome"] or "Desconhecido",
                "quantidade": it["quantidade"],
                "preco_unitario": it["preco_unitario"],
            }
        )

    result = []
    for r in pedidos_rows:
        result.append(
            {
                "id": r["id"],
                "usuario_id": r["usuario_id"],
                "status": r["status"],
                "total": r["total"],
                "criado_em": r["criado_em"],
                "itens": itens_por_pedido.get(r["id"], []),
            }
        )
    return result


class Pedido:
    @staticmethod
    def criar(usuario_id, itens):
        db = get_db()
        cursor = db.cursor()

        total = 0
        for item in itens:
            cursor.execute(
                "SELECT * FROM produtos WHERE id = ?", (item["produto_id"],)
            )
            produto = cursor.fetchone()
            if produto is None:
                return {"erro": "Produto " + str(item["produto_id"]) + " não encontrado"}
            if produto["estoque"] < item["quantidade"]:
                return {"erro": "Estoque insuficiente para " + produto["nome"]}
            total += produto["preco"] * item["quantidade"]

        cursor.execute(
            "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
            (usuario_id, total),
        )
        pedido_id = cursor.lastrowid

        for item in itens:
            cursor.execute(
                "SELECT preco FROM produtos WHERE id = ?", (item["produto_id"],)
            )
            produto = cursor.fetchone()
            cursor.execute(
                "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, "
                "preco_unitario) VALUES (?, ?, ?, ?)",
                (pedido_id, item["produto_id"], item["quantidade"], produto["preco"]),
            )
            cursor.execute(
                "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
                (item["quantidade"], item["produto_id"]),
            )

        db.commit()
        return {"pedido_id": pedido_id, "total": total}

    @staticmethod
    def por_usuario(usuario_id):
        return _carregar_pedidos("WHERE usuario_id = ?", (usuario_id,))

    @staticmethod
    def listar():
        return _carregar_pedidos()

    @staticmethod
    def atualizar_status(pedido_id, novo_status):
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "UPDATE pedidos SET status = ? WHERE id = ?", (novo_status, pedido_id)
        )
        db.commit()
        return True

    @staticmethod
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

        # REFACTORED: faixas de desconto extraídas para constante nomeada
        desconto = 0
        for limiar, percentual in FAIXAS_DESCONTO:
            if faturamento > limiar:
                desconto = faturamento * percentual
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
