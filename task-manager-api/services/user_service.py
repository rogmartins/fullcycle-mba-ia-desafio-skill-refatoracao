# REFACTORED: [HIGH] Regra de negócio de usuários fora das rotas.
import logging

from sqlalchemy.orm import joinedload

from database import db
from models.user import User
from models.task import Task
from constants import VALID_ROLES, MIN_PASSWORD_LENGTH
from utils.validators import is_valid_email
from utils.serializers import serialize_user_task_item
from services.errors import ServiceError

logger = logging.getLogger(__name__)


def list_users():
    # REFACTORED: eager loading evita N+1 ao contar tasks por usuário.
    users = User.query.options(joinedload(User.tasks)).all()
    result = []
    for u in users:
        data = u.to_dict()
        data['task_count'] = len(u.tasks)
        result.append(data)
    return result


def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        raise ServiceError(404, 'Usuário não encontrado')
    data = user.to_dict()
    data['tasks'] = [t.to_dict() for t in Task.query.filter_by(user_id=user_id).all()]
    return data


def create_user(data):
    if not data:
        raise ServiceError(400, 'Dados inválidos')

    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'user')

    if not name:
        raise ServiceError(400, 'Nome é obrigatório')
    if not email:
        raise ServiceError(400, 'Email é obrigatório')
    if not password:
        raise ServiceError(400, 'Senha é obrigatória')
    if not is_valid_email(email):
        raise ServiceError(400, 'Email inválido')
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ServiceError(400, 'Senha deve ter no mínimo 4 caracteres')
    if User.query.filter_by(email=email).first():
        raise ServiceError(409, 'Email já cadastrado')
    if role not in VALID_ROLES:
        raise ServiceError(400, 'Role inválido')

    user = User()
    user.name = name
    user.email = email
    user.set_password(password)
    user.role = role

    try:
        db.session.add(user)
        db.session.commit()
        logger.info("Usuário criado: %s - %s", user.id, user.name)
        return user.to_dict()
    except Exception as e:
        db.session.rollback()
        logger.error("Erro ao criar usuário: %s", e)
        raise ServiceError(500, 'Erro ao criar usuário')


def update_user(user_id, data):
    user = User.query.get(user_id)
    if not user:
        raise ServiceError(404, 'Usuário não encontrado')
    if not data:
        raise ServiceError(400, 'Dados inválidos')

    if 'name' in data:
        user.name = data['name']

    if 'email' in data:
        if not is_valid_email(data['email']):
            raise ServiceError(400, 'Email inválido')
        existing = User.query.filter_by(email=data['email']).first()
        if existing and existing.id != user_id:
            raise ServiceError(409, 'Email já cadastrado')
        user.email = data['email']

    if 'password' in data:
        if len(data['password']) < MIN_PASSWORD_LENGTH:
            raise ServiceError(400, 'Senha muito curta')
        user.set_password(data['password'])

    if 'role' in data:
        if data['role'] not in VALID_ROLES:
            raise ServiceError(400, 'Role inválido')
        user.role = data['role']

    if 'active' in data:
        user.active = data['active']

    try:
        db.session.commit()
        return user.to_dict()
    except Exception as e:
        db.session.rollback()
        logger.error("Erro ao atualizar usuário: %s", e)
        raise ServiceError(500, 'Erro ao atualizar')


def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        raise ServiceError(404, 'Usuário não encontrado')

    for t in Task.query.filter_by(user_id=user_id).all():
        db.session.delete(t)

    try:
        db.session.delete(user)
        db.session.commit()
        logger.info("Usuário deletado: %s", user_id)
    except Exception as e:
        db.session.rollback()
        logger.error("Erro ao deletar usuário: %s", e)
        raise ServiceError(500, 'Erro ao deletar')


def get_user_tasks(user_id):
    user = User.query.get(user_id)
    if not user:
        raise ServiceError(404, 'Usuário não encontrado')
    tasks = Task.query.filter_by(user_id=user_id).all()
    return [serialize_user_task_item(t) for t in tasks]


def login(data):
    if not data:
        raise ServiceError(400, 'Dados inválidos')

    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        raise ServiceError(400, 'Email e senha são obrigatórios')

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        raise ServiceError(401, 'Credenciais inválidas')
    if not user.active:
        raise ServiceError(403, 'Usuário inativo')

    return {
        'message': 'Login realizado com sucesso',
        'user': user.to_dict(),
        'token': 'fake-jwt-token-' + str(user.id),
    }
