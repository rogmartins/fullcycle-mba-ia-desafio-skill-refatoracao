import logging

from flask import Blueprint, request, jsonify

from models import pedido_model
from services import pedido_service, notification_service
from constants import STATUS_VALIDOS

logger = logging.getLogger(__name__)
pedidos_bp = Blueprint("pedidos", __name__)


@pedidos_bp.route("/pedidos", methods=["POST"])
def criar_pedido():
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({"erro": "Dados inválidos"}), 400

        usuario_id = dados.get("usuario_id")
        itens = dados.get("itens", [])
        if not usuario_id:
            return jsonify({"erro": "Usuario ID é obrigatório"}), 400
        if not itens or len(itens) == 0:
            return jsonify({"erro": "Pedido deve ter pelo menos 1 item"}), 400

        resultado = pedido_service.criar_pedido(usuario_id, itens)
        if "erro" in resultado:
            return jsonify({"erro": resultado["erro"], "sucesso": False}), 400

        return jsonify({
            "dados": resultado,
            "sucesso": True,
            "mensagem": "Pedido criado com sucesso",
        }), 201
    except Exception as e:
        logger.error("Erro ao criar pedido: %s", e)
        return jsonify({"erro": str(e)}), 500


@pedidos_bp.route("/pedidos", methods=["GET"])
def listar_todos_pedidos():
    try:
        return jsonify({"dados": pedido_model.get_pedidos(), "sucesso": True}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@pedidos_bp.route("/pedidos/usuario/<int:usuario_id>", methods=["GET"])
def listar_pedidos_usuario(usuario_id):
    try:
        return jsonify({"dados": pedido_model.get_pedidos(usuario_id), "sucesso": True}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@pedidos_bp.route("/pedidos/<int:pedido_id>/status", methods=["PUT"])
def atualizar_status_pedido(pedido_id):
    try:
        dados = request.get_json()
        novo_status = dados.get("status", "")
        if novo_status not in STATUS_VALIDOS:
            return jsonify({"erro": "Status inválido"}), 400

        pedido_model.atualizar_status(pedido_id, novo_status)
        notification_service.notificar_status_pedido(pedido_id, novo_status)
        return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
