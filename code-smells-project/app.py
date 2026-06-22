from flask import Flask, jsonify
from flask_cors import CORS
import config
from database import close_db, db_health_check  # REFACTORED: DB access via database module, not controller (AP-06)
from controllers.produtos import produtos_bp
from controllers.usuarios import usuarios_bp
from controllers.pedidos import pedidos_bp

app = Flask(__name__)
app.config["SECRET_KEY"] = config.SECRET_KEY  # REFACTORED: read from env via config module (AP-01)
app.config["DATABASE_PATH"] = config.DATABASE_PATH
app.config["DEBUG"] = config.DEBUG

CORS(app)
app.teardown_appcontext(close_db)  # REFACTORED: close per-request DB connection (AP-07)

app.register_blueprint(produtos_bp)
app.register_blueprint(usuarios_bp)
app.register_blueprint(pedidos_bp)


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
            "health": "/health"
        }
    })


@app.route("/health")
def health_check():
    try:
        counts = db_health_check()  # REFACTORED: DB access via database module (AP-06)
        return jsonify({
            "status": "ok",
            "database": "connected",
            "counts": counts,
            "versao": "1.0.0",
            # REFACTORED: removed secret_key, debug, db_path from response (AP-04)
        }), 200
    except Exception as e:
        return jsonify({"status": "erro", "detalhes": str(e)}), 500


# REFACTORED: removed /admin/query endpoint — arbitrary SQL execution from user input (AP-02)
# REFACTORED: removed /admin/reset-db endpoint — destructive admin ops belong in migrations


if __name__ == "__main__":
    print("=" * 50)
    print("SERVIDOR INICIADO")
    print("Rodando em http://localhost:5000")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5000, debug=config.DEBUG)
