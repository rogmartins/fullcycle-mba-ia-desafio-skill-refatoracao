import logging
from flask import Flask, jsonify
from flask_cors import CORS

from config import SECRET_KEY, DEBUG  # REFACTORED: secrets loaded from environment via config.py
from database import get_db, close_db
from controllers.produtos import produtos_bp
from controllers.usuarios import usuarios_bp, login as login_view
from controllers.pedidos import pedidos_bp
from controllers.relatorios import relatorios_bp

logging.basicConfig(level=logging.INFO)  # REFACTORED: structured logging configured at app level

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY  # REFACTORED: no hardcoded secret
app.config["DEBUG"] = DEBUG            # REFACTORED: no hardcoded DEBUG=True
CORS(app)

# REFACTORED: per-request DB connection teardown
app.teardown_appcontext(close_db)

# Register Blueprints — routes preserved for API contract compatibility
app.register_blueprint(produtos_bp, url_prefix="/produtos")
app.register_blueprint(usuarios_bp, url_prefix="/usuarios")
app.register_blueprint(pedidos_bp, url_prefix="/pedidos")
app.register_blueprint(relatorios_bp, url_prefix="/relatorios")

# /login preserves the original API contract — delegates to the usuarios blueprint handler
app.add_url_rule("/login", "login", login_view, methods=["POST"])


@app.route("/")
def index():
    return jsonify({
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
    })


@app.route("/health")
def health_check():
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT 1")
        cursor.execute("SELECT COUNT(*) FROM produtos")
        produtos = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        usuarios = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM pedidos")
        pedidos = cursor.fetchone()[0]

        # REFACTORED: secret_key, debug, and db_path removed from public health response
        return jsonify({
            "status": "ok",
            "database": "connected",
            "counts": {"produtos": produtos, "usuarios": usuarios, "pedidos": pedidos},
            "versao": "1.0.0",
        }), 200
    except Exception as e:
        return jsonify({"status": "erro", "detalhes": str(e)}), 500


# REFACTORED: /admin/reset-db and /admin/query endpoints removed —
#   both allowed unauthenticated arbitrary data destruction and SQL execution


if __name__ == "__main__":
    with app.app_context():
        get_db()
    print("=" * 50)
    print("SERVIDOR INICIADO")
    print("Rodando em http://localhost:5000")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5000, debug=DEBUG)
