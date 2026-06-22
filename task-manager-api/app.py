from flask import Flask
from flask_cors import CORS
from database import db
from config import SECRET_KEY, DATABASE_URI, DEBUG
from routes.task_routes import task_bp
from routes.user_routes import user_bp
from routes.report_routes import report_bp
from routes.category_routes import category_bp
from datetime import datetime, timezone

app = Flask(__name__)

# REFACTORED: configurações lidas de config.py que usa variáveis de ambiente (AP-01)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = SECRET_KEY

CORS(app)
db.init_app(app)

app.register_blueprint(task_bp)
app.register_blueprint(user_bp)
app.register_blueprint(report_bp)
# REFACTORED: blueprint de categorias extraído do report_bp (AP-04)
app.register_blueprint(category_bp)

@app.route('/health')
def health():
    return {'status': 'ok', 'timestamp': str(datetime.now(timezone.utc))}

@app.route('/')
def index():
    return {'message': 'Task Manager API', 'version': '1.0'}

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
