import logging

# REFACTORED: efeitos colaterais de notificação extraídos do controller para um
# serviço dedicado (corrige lógica de domínio/infra dentro do controller)

logger = logging.getLogger(__name__)


def notificar_pedido_criado(pedido_id, usuario_id):
    logger.info("EMAIL: pedido %s criado para usuario %s", pedido_id, usuario_id)
    logger.info("SMS: seu pedido foi recebido!")
    logger.info("PUSH: novo pedido recebido pelo sistema")


def notificar_status_pedido(pedido_id, novo_status):
    if novo_status == "aprovado":
        logger.info("NOTIFICACAO: pedido %s aprovado, preparar envio", pedido_id)
    elif novo_status == "cancelado":
        logger.info("NOTIFICACAO: pedido %s cancelado, devolver estoque", pedido_id)
