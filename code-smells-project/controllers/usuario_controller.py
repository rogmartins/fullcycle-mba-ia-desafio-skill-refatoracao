import logging

from flask import Blueprint, request, jsonify

from models import usuario_model
from controllers.validators import email_valido

logger = logging.getLogger(__name__)
usuarios_bp = Blueprint("usuarios", __name__)


@usuarios_bp.route("/usuarios", methods=["GET"])
def listar_usuarios():
    try:
        return jsonify({"dados": usuario_model.get_todos(), "sucesso": True}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@usuarios_bp.route("/usuarios/<int:id>", methods=["GET"])
def buscar_usuario(id):
    try:
        usuario = usuario_model.get_por_id(id)
        if usuario:
            return jsonify({"dados": usuario, "sucesso": True}), 200
        return jsonify({"erro": "Usuário não encontrado"}), 404
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@usuarios_bp.route("/usuarios", methods=["POST"])
def criar_usuario():
    try:
        dados = request.get_json()
        if not dados:
            return jsonify({"erro": "Dados inválidos"}), 400

        nome = dados.get("nome", "")
        email = dados.get("email", "")
        senha = dados.get("senha", "")

        if not nome or not email or not senha:
            return jsonify({"erro": "Nome, email e senha são obrigatórios"}), 400
        # REFACTORED: [MEDIUM] Validação de formato de email antes de persistir.
        if not email_valido(email):
            return jsonify({"erro": "Email inválido"}), 400

        id = usuario_model.criar(nome, email, senha)
        logger.info("Usuário criado: %s", email)
        return jsonify({"dados": {"id": id}, "sucesso": True}), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@usuarios_bp.route("/login", methods=["POST"])
def login():
    try:
        dados = request.get_json()
        email = dados.get("email", "")
        senha = dados.get("senha", "")

        if not email or not senha:
            return jsonify({"erro": "Email e senha são obrigatórios"}), 400

        usuario = usuario_model.autenticar(email, senha)
        if usuario:
            logger.info("Login bem-sucedido: %s", email)
            return jsonify({"dados": usuario, "sucesso": True, "mensagem": "Login OK"}), 200

        logger.info("Login falhou: %s", email)
        return jsonify({"erro": "Email ou senha inválidos", "sucesso": False}), 401
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
