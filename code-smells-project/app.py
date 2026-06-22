import logging

from flask import Flask, jsonify
from flask_cors import CORS

import database
from config import Config
from routes.routes import register_routes

# REFACTORED: entry point enxuto — application factory, config externa,
# error handling centralizado e roteamento delegado à camada de rotas.
# Endpoints /admin/query (SQL arbitrário) e /admin/reset-db (destrutivo sem auth)
# foram REMOVIDOS por serem vulnerabilidades CRITICAL/HIGH.

logging.basicConfig(level=logging.INFO)


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    database.init_db()
    database.init_app(app)

    register_routes(app)

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"erro": "Recurso não encontrado"}), 404

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"erro": "Erro interno do servidor"}), 500

    @app.errorhandler(Exception)
    def unhandled(e):
        app.logger.exception("Erro não tratado: %s", e)
        return jsonify({"erro": "Erro interno do servidor"}), 500

    return app


app = create_app()


if __name__ == "__main__":
    print("=" * 50)
    print("SERVIDOR INICIADO")
    print("Rodando em http://localhost:%s" % Config.PORT)
    print("=" * 50)
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
