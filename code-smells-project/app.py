# REFACTORED: [HIGH] app.py enxuto — apenas cria a app e registra os blueprints.
import logging

from flask import Flask
from flask_cors import CORS

from config import Config
from database import init_db, close_db
from controllers.produto_controller import produtos_bp
from controllers.usuario_controller import usuarios_bp
from controllers.pedido_controller import pedidos_bp
from controllers.sistema_controller import sistema_bp

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    app.teardown_appcontext(close_db)

    app.register_blueprint(produtos_bp)
    app.register_blueprint(usuarios_bp)
    app.register_blueprint(pedidos_bp)
    app.register_blueprint(sistema_bp)

    with app.app_context():
        init_db()

    return app


app = create_app()


if __name__ == "__main__":
    print("=" * 50)
    print("SERVIDOR INICIADO")
    print("Rodando em http://localhost:5000")
    print("=" * 50)
    app.run(host="0.0.0.0", port=5000, debug=Config.DEBUG)
