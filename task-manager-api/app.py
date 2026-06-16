from flask import Flask
from flask_cors import CORS
from database import db
from routes.task_routes import task_bp
from routes.user_routes import user_bp
from routes.report_routes import report_bp
import config
import datetime

app = Flask(__name__)

# REFACTORED: credenciais carregadas de variáveis de ambiente via config.py
app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = config.SECRET_KEY

CORS(app)
db.init_app(app)

app.register_blueprint(task_bp)
app.register_blueprint(user_bp)
app.register_blueprint(report_bp)

@app.route('/health')
def health():
    return {'status': 'ok', 'timestamp': str(datetime.datetime.now())}

@app.route('/')
def index():
    return {'message': 'Task Manager API', 'version': '1.0'}

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
