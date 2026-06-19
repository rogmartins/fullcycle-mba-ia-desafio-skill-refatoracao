# REFACTORED: [HIGH] Regra de negócio do pedido fora da camada de dados (antes models.py:133).
from models import produto_model, pedido_model
from services import notification_service


def criar_pedido(usuario_id, itens):
    """Valida estoque, calcula total, persiste o pedido e dispara notificações.

    Retorna {"pedido_id", "total"} em caso de sucesso ou {"erro"} caso contrário.
    """
    total = 0
    linhas = []

    for item in itens:
        # REFACTORED: [MEDIUM] Validação da estrutura do item antes de processar.
        if "produto_id" not in item or "quantidade" not in item:
            return {"erro": "Item inválido: produto_id e quantidade são obrigatórios"}

        produto = produto_model.get_por_id(item["produto_id"])
        if produto is None:
            return {"erro": "Produto " + str(item["produto_id"]) + " não encontrado"}
        if produto["estoque"] < item["quantidade"]:
            return {"erro": "Estoque insuficiente para " + produto["nome"]}

        total += produto["preco"] * item["quantidade"]
        linhas.append((produto["id"], item["quantidade"], produto["preco"]))

    pedido_id = pedido_model.criar(usuario_id, total, linhas)
    notification_service.notificar_pedido_criado(pedido_id, usuario_id)
    return {"pedido_id": pedido_id, "total": total}
