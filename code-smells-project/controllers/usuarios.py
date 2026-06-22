from flask import Blueprint, request, jsonify
import models.usuario as usuario_model

usuarios_bp = Blueprint("usuarios", __name__)


@usuarios_bp.route("/usuarios", methods=["GET"])
def listar_usuarios():
    try:
        usuarios = usuario_model.get_todos_usuarios()
        return jsonify({"dados": usuarios, "sucesso": True}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@usuarios_bp.route("/usuarios/<int:id>", methods=["GET"])
def buscar_usuario(id):
    try:
        usuario = usuario_model.get_usuario_por_id(id)
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
        id = usuario_model.criar_usuario(nome, email, senha)
        return jsonify({"dados": {"id": id}, "sucesso": True}), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@usuarios_bp.route("/login", methods=["POST"])
def login():
    try:
        dados = request.get_json(silent=True)  # REFACTORED: silent=True returns None instead of 415 for wrong Content-Type (AP-09)
        if not dados:  # REFACTORED: null check before .get() prevents AttributeError (AP-09)
            return jsonify({"erro": "Corpo da requisição inválido"}), 400
        email = dados.get("email", "")
        senha = dados.get("senha", "")
        if not email or not senha:
            return jsonify({"erro": "Email e senha são obrigatórios"}), 400
        usuario = usuario_model.login_usuario(email, senha)
        if usuario:
            return jsonify({"dados": usuario, "sucesso": True, "mensagem": "Login OK"}), 200
        return jsonify({"erro": "Email ou senha inválidos", "sucesso": False}), 401
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
