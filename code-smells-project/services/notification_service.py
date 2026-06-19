# REFACTORED: [HIGH] Notificações isoladas em serviço (antes prints embutidos no controller).
import logging

logger = logging.getLogger(__name__)


def notificar_pedido_criado(pedido_id, usuario_id):
    logger.info("ENVIANDO EMAIL: Pedido %s criado para usuario %s", pedido_id, usuario_id)
    logger.info("ENVIANDO SMS: Seu pedido foi recebido!")
    logger.info("ENVIANDO PUSH: Novo pedido recebido pelo sistema")


def notificar_status_pedido(pedido_id, novo_status):
    if novo_status == "aprovado":
        logger.info("NOTIFICACAO: Pedido %s foi aprovado! Preparar envio.", pedido_id)
    elif novo_status == "cancelado":
        logger.info("NOTIFICACAO: Pedido %s cancelado. Devolver estoque.", pedido_id)
