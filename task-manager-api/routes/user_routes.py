from flask import Blueprint, request, jsonify
from database import db
from models.user import User
from models.task import Task
from datetime import datetime, timedelta, timezone
# REFACTORED: validate_email importado de helpers — elimina regex duplicada
from utils.helpers import validate_email
# REFACTORED: constantes importadas de helpers — elimina números mágicos
from utils.helpers import VALID_ROLES, MIN_PASSWORD_LENGTH
import jwt
import config

user_bp = Blueprint('users', __name__)

@user_bp.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    result = []
    for u in users:
        user_data = {
            'id': u.id,
            'name': u.name,
            'email': u.email,
            'role': u.role,
            'active': u.active,
            'created_at': str(u.created_at),
            'task_count': len(u.tasks)
        }
        result.append(user_data)
    return jsonify(result), 200

@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404

    data = user.to_dict()

    tasks = Task.query.filter_by(user_id=user_id).all()
    data['tasks'] = [t.to_dict() for t in tasks]

    return jsonify(data), 200

@user_bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400

    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'user')

    if not name:
        return jsonify({'error': 'Nome é obrigatório'}), 400
    if not email:
        return jsonify({'error': 'Email é obrigatório'}), 400
    if not password:
        return jsonify({'error': 'Senha é obrigatória'}), 400

    # REFACTORED: validate_email() de helpers substitui regex duplicada
    if not validate_email(email):
        return jsonify({'error': 'Email inválido'}), 400

    # REFACTORED: MIN_PASSWORD_LENGTH de helpers substitui número mágico
    if len(password) < MIN_PASSWORD_LENGTH:
        return jsonify({'error': f'Senha deve ter no mínimo {MIN_PASSWORD_LENGTH} caracteres'}), 400

    existing = User.query.filter_by(email=email).first()
    if existing:
        return jsonify({'error': 'Email já cadastrado'}), 409

    if role not in VALID_ROLES:
        return jsonify({'error': 'Role inválido'}), 400

    user = User()
    user.name = name
    user.email = email
    user.set_password(password)
    user.role = role

    try:
        db.session.add(user)
        db.session.commit()
        print(f"Usuário criado: {user.id} - {user.name}")
        return jsonify(user.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        print(f"ERRO: {str(e)}")
        return jsonify({'error': 'Erro ao criar usuário'}), 500

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400

    if 'name' in data:
        user.name = data['name']

    if 'email' in data:
        # REFACTORED: validate_email() de helpers substitui regex duplicada
        if not validate_email(data['email']):
            return jsonify({'error': 'Email inválido'}), 400

        existing = User.query.filter_by(email=data['email']).first()
        if existing and existing.id != user_id:
            return jsonify({'error': 'Email já cadastrado'}), 409
        user.email = data['email']

    if 'password' in data:
        if len(data['password']) < MIN_PASSWORD_LENGTH:
            return jsonify({'error': 'Senha muito curta'}), 400
        user.set_password(data['password'])

    if 'role' in data:
        if data['role'] not in VALID_ROLES:
            return jsonify({'error': 'Role inválido'}), 400
        user.role = data['role']

    if 'active' in data:
        user.active = data['active']

    try:
        db.session.commit()
        return jsonify(user.to_dict()), 200
    except:
        db.session.rollback()
        return jsonify({'error': 'Erro ao atualizar'}), 500

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404

    tasks = Task.query.filter_by(user_id=user_id).all()
    for t in tasks:
        db.session.delete(t)

    try:
        db.session.delete(user)
        db.session.commit()
        print(f"Usuário deletado: {user_id}")
        return jsonify({'message': 'Usuário deletado com sucesso'}), 200
    except:
        db.session.rollback()
        return jsonify({'error': 'Erro ao deletar'}), 500

@user_bp.route('/users/<int:user_id>/tasks', methods=['GET'])
def get_user_tasks(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404

    tasks = Task.query.filter_by(user_id=user_id).all()
    result = []
    for t in tasks:
        task_data = {
            'id': t.id,
            'title': t.title,
            'description': t.description,
            'status': t.status,
            'priority': t.priority,
            'created_at': str(t.created_at),
            'due_date': str(t.due_date) if t.due_date else None,
            # REFACTORED: Task.is_overdue() substitui lógica de overdue duplicada
            'overdue': t.is_overdue()
        }
        result.append(task_data)

    return jsonify(result), 200

@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email e senha são obrigatórios'}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'Credenciais inválidas'}), 401

    if not user.check_password(password):
        return jsonify({'error': 'Credenciais inválidas'}), 401

    if not user.active:
        return jsonify({'error': 'Usuário inativo'}), 403

    # REFACTORED: JWT real assinado com SECRET_KEY substitui token falso
    payload = {
        'sub': user.id,
        'email': user.email,
        'role': user.role,
        'exp': datetime.now(timezone.utc) + timedelta(hours=config.JWT_EXPIRATION_HOURS)
    }
    token = jwt.encode(payload, config.SECRET_KEY, algorithm='HS256')

    return jsonify({
        'message': 'Login realizado com sucesso',
        'user': user.to_dict(),
        'token': token
    }), 200
