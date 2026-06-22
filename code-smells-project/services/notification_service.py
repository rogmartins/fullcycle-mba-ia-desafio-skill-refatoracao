# REFACTORED: notification business logic extracted from controllers.py:208 and :247 (AP-04)

def pedido_criado(pedido_id, usuario_id):
    print(f"ENVIANDO EMAIL: Pedido {pedido_id} criado para usuario {usuario_id}")
    print("ENVIANDO SMS: Seu pedido foi recebido!")
    print("ENVIANDO PUSH: Novo pedido recebido pelo sistema")


def pedido_status_atualizado(pedido_id, novo_status):
    if novo_status == "aprovado":
        print(f"NOTIFICAÇÃO: Pedido {pedido_id} foi aprovado! Preparar envio.")
    if novo_status == "cancelado":
        print(f"NOTIFICAÇÃO: Pedido {pedido_id} cancelado. Devolver estoque.")
