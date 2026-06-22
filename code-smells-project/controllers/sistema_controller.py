from flask import jsonify

from database import get_db

# REFACTORED: endpoints de sistema (index/health) sem exposição de dados sensíveis


def index():
    return jsonify(
        {
            "mensagem": "Bem-vindo à API da Loja",
            "versao": "1.0.0",
            "endpoints": {
                "produtos": "/produtos",
                "usuarios": "/usuarios",
                "pedidos": "/pedidos",
                "login": "/login",
                "relatorios": "/relatorios/vendas",
                "health": "/health",
            },
        }
    )


def health_check():
    try:
        cursor = get_db().cursor()
        cursor.execute("SELECT COUNT(*) FROM produtos")
        produtos = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        usuarios = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM pedidos")
        pedidos = cursor.fetchone()[0]

        # REFACTORED: removidos secret_key/db_path/debug da resposta
        return jsonify(
            {
                "status": "ok",
                "database": "connected",
                "counts": {"produtos": produtos, "usuarios": usuarios, "pedidos": pedidos},
                "versao": "1.0.0",
            }
        ), 200
    except Exception as e:
        return jsonify({"status": "erro", "detalhes": str(e)}), 500
