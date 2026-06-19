import logging

from flask import Blueprint, request, jsonify

from database import get_db
from models import pedido_model
from config import Config

logger = logging.getLogger(__name__)
sistema_bp = Blueprint("sistema", __name__)


@sistema_bp.route("/")
def index():
    return jsonify({
        "mensagem": "Bem-vindo à API da Loja",
        "versao": Config.VERSAO,
        "endpoints": {
            "produtos": "/produtos",
            "usuarios": "/usuarios",
            "pedidos": "/pedidos",
            "login": "/login",
            "relatorios": "/relatorios/vendas",
            "health": "/health",
        },
    })


@sistema_bp.route("/relatorios/vendas", methods=["GET"])
def relatorio_vendas():
    try:
        return jsonify({"dados": pedido_model.relatorio_vendas(), "sucesso": True}), 200
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@sistema_bp.route("/health", methods=["GET"])
def health_check():
    try:
        cursor = get_db().cursor()
        cursor.execute("SELECT 1")
        cursor.execute("SELECT COUNT(*) FROM produtos")
        produtos = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        usuarios = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM pedidos")
        pedidos = cursor.fetchone()[0]

        # REFACTORED: [CRITICAL] secret_key e debug removidos do payload (antes controllers.py:289).
        return jsonify({
            "status": "ok",
            "database": "connected",
            "counts": {"produtos": produtos, "usuarios": usuarios, "pedidos": pedidos},
            "versao": Config.VERSAO,
            "ambiente": Config.AMBIENTE,
            "db_path": Config.DB_PATH,
        }), 200
    except Exception as e:
        return jsonify({"status": "erro", "detalhes": str(e)}), 500


@sistema_bp.route("/admin/reset-db", methods=["POST"])
def reset_database():
    # REFACTORED: [HIGH] Rota destrutiva protegida por token (antes sem autenticação).
    if not Config.ADMIN_TOKEN or request.headers.get("X-Admin-Token") != Config.ADMIN_TOKEN:
        return jsonify({"erro": "Não autorizado"}), 401

    db = get_db()
    cursor = db.cursor()
    for tabela in ("itens_pedido", "pedidos", "produtos", "usuarios"):
        cursor.execute("DELETE FROM " + tabela)
    db.commit()
    logger.warning("BANCO DE DADOS RESETADO via /admin/reset-db")
    return jsonify({"mensagem": "Banco de dados resetado", "sucesso": True}), 200
