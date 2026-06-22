from flask import Blueprint, request, jsonify
from database import db
from models.user import User
from models.task import Task
import re
import secrets

user_bp = Blueprint('users', __name__)


@user_bp.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    result = [{
        'id': u.id,
        'name': u.name,
        'email': u.email,
        'role': u.role,
        'active': u.active,
        'created_at': str(u.created_at),
        'task_count': len(u.tasks)
    } for u in users]
    return jsonify(result), 200


@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404

    # REFACTORED: to_dict() não expõe mais o campo password (AP-04)
    data = user.to_dict()
    data['tasks'] = [t.to_dict() for t in Task.query.filter_by(user_id=user_id).all()]
    return jsonify(data), 200


@user_bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json(silent=True)
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

    if not re.match(r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$', email):
        return jsonify({'error': 'Email inválido'}), 400
    if len(password) < 4:
        return jsonify({'error': 'Senha deve ter no mínimo 4 caracteres'}), 400
    if role not in ['user', 'admin', 'manager']:
        return jsonify({'error': 'Role inválido'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email já cadastrado'}), 409

    user = User(name=name, email=email, role=role)
    user.set_password(password)

    try:
        db.session.add(user)
        db.session.commit()
        return jsonify(user.to_dict()), 201
    except Exception:
        db.session.rollback()
        return jsonify({'error': 'Erro ao criar usuário'}), 500


@user_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400

    if 'name' in data:
        user.name = data['name']

    if 'email' in data:
        if not re.match(r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$', data['email']):
            return jsonify({'error': 'Email inválido'}), 400
        existing = User.query.filter_by(email=data['email']).first()
        if existing and existing.id != user_id:
            return jsonify({'error': 'Email já cadastrado'}), 409
        user.email = data['email']

    if 'password' in data:
        if len(data['password']) < 4:
            return jsonify({'error': 'Senha muito curta'}), 400
        user.set_password(data['password'])

    if 'role' in data:
        if data['role'] not in ['user', 'admin', 'manager']:
            return jsonify({'error': 'Role inválido'}), 400
        user.role = data['role']

    if 'active' in data:
        user.active = data['active']

    try:
        db.session.commit()
        return jsonify(user.to_dict()), 200
    except Exception:
        db.session.rollback()
        return jsonify({'error': 'Erro ao atualizar'}), 500


@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404

    Task.query.filter_by(user_id=user_id).delete()
    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'Usuário deletado com sucesso'}), 200
    except Exception:
        db.session.rollback()
        return jsonify({'error': 'Erro ao deletar'}), 500


@user_bp.route('/users/<int:user_id>/tasks', methods=['GET'])
def get_user_tasks(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404

    tasks = Task.query.filter_by(user_id=user_id).all()
    result = []
    for t in tasks:
        data = t.to_dict()
        # REFACTORED: is_overdue() centralizado no modelo (AP-13)
        data['overdue'] = t.is_overdue()
        result.append(data)
    return jsonify(result), 200


@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400

    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'error': 'Email e senha são obrigatórios'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'Credenciais inválidas'}), 401

    if not user.active:
        return jsonify({'error': 'Usuário inativo'}), 403

    # REFACTORED: token aleatório criptograficamente seguro (AP-04)
    token = secrets.token_hex(32)

    return jsonify({
        'message': 'Login realizado com sucesso',
        'user': user.to_dict(),
        'token': token
    }), 200
