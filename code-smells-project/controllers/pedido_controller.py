from flask import jsonify, request

from constants import STATUS_VALIDOS
from models.pedido import Pedido
from services import notification_service

# REFACTORED: controller fino de pedidos; notificações delegadas ao serviço


def criar_pedido():
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "Dados inválidos"}), 400

    usuario_id = dados.get("usuario_id")
    itens = dados.get("itens", [])
    if not usuario_id:
        return jsonify({"erro": "Usuario ID é obrigatório"}), 400
    if not itens or len(itens) == 0:
        return jsonify({"erro": "Pedido deve ter pelo menos 1 item"}), 400

    resultado = Pedido.criar(usuario_id, itens)
    if "erro" in resultado:
        return jsonify({"erro": resultado["erro"], "sucesso": False}), 400

    notification_service.notificar_pedido_criado(resultado["pedido_id"], usuario_id)
    return jsonify({"dados": resultado, "sucesso": True, "mensagem": "Pedido criado com sucesso"}), 201


def listar_pedidos_usuario(usuario_id):
    return jsonify({"dados": Pedido.por_usuario(usuario_id), "sucesso": True}), 200


def listar_todos_pedidos():
    return jsonify({"dados": Pedido.listar(), "sucesso": True}), 200


def atualizar_status_pedido(pedido_id):
    dados = request.get_json()
    novo_status = dados.get("status", "") if dados else ""
    if novo_status not in STATUS_VALIDOS:
        return jsonify({"erro": "Status inválido"}), 400

    Pedido.atualizar_status(pedido_id, novo_status)
    notification_service.notificar_status_pedido(pedido_id, novo_status)
    return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200


def relatorio_vendas():
    return jsonify({"dados": Pedido.relatorio_vendas(), "sucesso": True}), 200
