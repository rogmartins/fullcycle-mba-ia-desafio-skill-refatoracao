import logging

# REFACTORED: notification side effects extracted from controller into dedicated service
logger = logging.getLogger(__name__)


def notificar_pedido_criado(pedido_id, usuario_id):
    logger.info("EMAIL: Pedido %s criado para usuario %s", pedido_id, usuario_id)
    logger.info("SMS: Seu pedido %s foi recebido!", pedido_id)
    logger.info("PUSH: Novo pedido %s recebido pelo sistema", pedido_id)


def notificar_status_atualizado(pedido_id, novo_status):
    if novo_status == "aprovado":
        logger.info("NOTIFICAÇÃO: Pedido %s aprovado. Preparar envio.", pedido_id)
    elif novo_status == "cancelado":
        logger.info("NOTIFICAÇÃO: Pedido %s cancelado. Devolver estoque.", pedido_id)
