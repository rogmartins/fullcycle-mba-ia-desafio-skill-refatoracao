import logging
from flask import Blueprint, request, jsonify
from models.pedido import (
    criar_pedido as model_criar_pedido,
    get_pedidos_usuario, get_todos_pedidos,
    atualizar_status_pedido as model_atualizar_status,
)
from services.notifications import notificar_pedido_criado, notificar_status_atualizado

logger = logging.getLogger(__name__)  # REFACTORED: structured logging replaces print()
pedidos_bp = Blueprint("pedidos", __name__)

_STATUS_VALIDOS = ["pendente", "aprovado", "enviado", "entregue", "cancelado"]


@pedidos_bp.route("", methods=["POST"])
def criar_pedido():
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({"erro": "Dados inválidos"}), 400

        usuario_id = dados.get("usuario_id")
        itens = dados.get("itens", [])

        if not usuario_id:
            return jsonify({"erro": "Usuario ID é obrigatório"}), 400
        if not itens:
            return jsonify({"erro": "Pedido deve ter pelo menos 1 item"}), 400

        resultado = model_criar_pedido(usuario_id, itens)
        if "erro" in resultado:
            return jsonify({"erro": resultado["erro"], "sucesso": False}), 400

        notificar_pedido_criado(resultado["pedido_id"], usuario_id)  # REFACTORED: notification delegated to service layer
        return jsonify({"dados": resultado, "sucesso": True, "mensagem": "Pedido criado com sucesso"}), 201
    except Exception as e:
        logger.error("Erro crítico ao criar pedido: %s", e)
        return jsonify({"erro": str(e)}), 500


@pedidos_bp.route("", methods=["GET"])
def listar_todos_pedidos():
    try:
        pedidos = get_todos_pedidos()
        return jsonify({"dados": pedidos, "sucesso": True}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@pedidos_bp.route("/usuario/<int:usuario_id>", methods=["GET"])
def listar_pedidos_usuario(usuario_id):
    try:
        pedidos = get_pedidos_usuario(usuario_id)
        return jsonify({"dados": pedidos, "sucesso": True}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@pedidos_bp.route("/<int:pedido_id>/status", methods=["PUT"])
def atualizar_status_pedido(pedido_id):
    try:
        dados = request.get_json()
        novo_status = dados.get("status", "")

        if novo_status not in _STATUS_VALIDOS:
            return jsonify({"erro": "Status inválido"}), 400

        model_atualizar_status(pedido_id, novo_status)
        notificar_status_atualizado(pedido_id, novo_status)  # REFACTORED: notification delegated to service layer
        return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
