from flask import Blueprint, request, jsonify
import models.pedido as pedido_model
import services.notification_service as notification_service  # REFACTORED: injected service (AP-04)

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
        if not itens:
            return jsonify({"erro": "Pedido deve ter pelo menos 1 item"}), 400
        resultado = pedido_model.criar_pedido(usuario_id, itens)
        if "erro" in resultado:
            return jsonify({"erro": resultado["erro"], "sucesso": False}), 400
        notification_service.pedido_criado(resultado["pedido_id"], usuario_id)  # REFACTORED: delegated to service (AP-04)
        return jsonify({"dados": resultado, "sucesso": True, "mensagem": "Pedido criado com sucesso"}), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@pedidos_bp.route("/pedidos", methods=["GET"])
def listar_todos_pedidos():
    try:
        pedidos = pedido_model.get_todos_pedidos()
        return jsonify({"dados": pedidos, "sucesso": True}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@pedidos_bp.route("/pedidos/usuario/<int:usuario_id>", methods=["GET"])
def listar_pedidos_usuario(usuario_id):
    try:
        pedidos = pedido_model.get_pedidos_usuario(usuario_id)
        return jsonify({"dados": pedidos, "sucesso": True}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@pedidos_bp.route("/pedidos/<int:pedido_id>/status", methods=["PUT"])
def atualizar_status_pedido(pedido_id):
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({"erro": "Dados inválidos"}), 400
        novo_status = dados.get("status", "")
        if novo_status not in ["pendente", "aprovado", "enviado", "entregue", "cancelado"]:
            return jsonify({"erro": "Status inválido"}), 400
        pedido_model.atualizar_status_pedido(pedido_id, novo_status)
        notification_service.pedido_status_atualizado(pedido_id, novo_status)  # REFACTORED: delegated to service (AP-04)
        return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@pedidos_bp.route("/relatorios/vendas", methods=["GET"])
def relatorio_vendas():
    try:
        relatorio = pedido_model.relatorio_vendas()
        return jsonify({"dados": relatorio, "sucesso": True}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
