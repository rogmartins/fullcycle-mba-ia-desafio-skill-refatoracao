# REFACTORED: [HIGH] Regra de negócio das tasks fora das rotas.
import logging
from datetime import datetime, timedelta

from sqlalchemy.orm import joinedload

from database import db
from models.task import Task
from models.user import User
from models.category import Category
from constants import (
    VALID_STATUSES, TERMINAL_STATUSES, MIN_TITLE_LENGTH, MAX_TITLE_LENGTH,
    MIN_PRIORITY, MAX_PRIORITY, DEFAULT_PRIORITY,
)
from utils.serializers import serialize_task_list_item, serialize_task_detail
from services.errors import ServiceError

logger = logging.getLogger(__name__)


def list_tasks():
    # REFACTORED: [HIGH] Eager loading elimina o N+1 de user/category por task.
    tasks = Task.query.options(joinedload(Task.user), joinedload(Task.category)).all()
    return [serialize_task_list_item(t) for t in tasks]


def get_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        raise ServiceError(404, 'Task não encontrada')
    return serialize_task_detail(task)


def _parse_due_date(value, error_msg):
    try:
        return datetime.strptime(value, '%Y-%m-%d')
    except (ValueError, TypeError):
        raise ServiceError(400, error_msg)


def _check_refs(user_id, category_id):
    if user_id:
        if not User.query.get(user_id):
            raise ServiceError(404, 'Usuário não encontrado')
    if category_id:
        if not Category.query.get(category_id):
            raise ServiceError(404, 'Categoria não encontrada')


def create_task(data):
    if not data:
        raise ServiceError(400, 'Dados inválidos')

    title = data.get('title')
    if not title:
        raise ServiceError(400, 'Título é obrigatório')
    if len(title) < MIN_TITLE_LENGTH:
        raise ServiceError(400, 'Título muito curto')
    if len(title) > MAX_TITLE_LENGTH:
        raise ServiceError(400, 'Título muito longo')

    status = data.get('status', 'pending')
    priority = data.get('priority', DEFAULT_PRIORITY)
    user_id = data.get('user_id')
    category_id = data.get('category_id')
    due_date = data.get('due_date')
    tags = data.get('tags')

    if status not in VALID_STATUSES:
        raise ServiceError(400, 'Status inválido')
    if priority < MIN_PRIORITY or priority > MAX_PRIORITY:
        raise ServiceError(400, 'Prioridade deve ser entre 1 e 5')

    _check_refs(user_id, category_id)

    task = Task()
    task.title = title
    task.description = data.get('description', '')
    task.status = status
    task.priority = priority
    task.user_id = user_id
    task.category_id = category_id

    if due_date:
        task.due_date = _parse_due_date(due_date, 'Formato de data inválido. Use YYYY-MM-DD')

    if tags:
        task.tags = ','.join(tags) if isinstance(tags, list) else tags

    try:
        db.session.add(task)
        db.session.commit()
        logger.info("Task criada: %s - %s", task.id, task.title)
        return task.to_dict()
    except Exception as e:
        db.session.rollback()
        logger.error("Erro ao criar task: %s", e)
        raise ServiceError(500, 'Erro ao criar task')


def update_task(task_id, data):
    task = Task.query.get(task_id)
    if not task:
        raise ServiceError(404, 'Task não encontrada')
    if not data:
        raise ServiceError(400, 'Dados inválidos')

    if 'title' in data:
        if len(data['title']) < MIN_TITLE_LENGTH:
            raise ServiceError(400, 'Título muito curto')
        if len(data['title']) > MAX_TITLE_LENGTH:
            raise ServiceError(400, 'Título muito longo')
        task.title = data['title']

    if 'description' in data:
        task.description = data['description']

    if 'status' in data:
        if data['status'] not in VALID_STATUSES:
            raise ServiceError(400, 'Status inválido')
        task.status = data['status']

    if 'priority' in data:
        if data['priority'] < MIN_PRIORITY or data['priority'] > MAX_PRIORITY:
            raise ServiceError(400, 'Prioridade deve ser entre 1 e 5')
        task.priority = data['priority']

    if 'user_id' in data:
        if data['user_id'] and not User.query.get(data['user_id']):
            raise ServiceError(404, 'Usuário não encontrado')
        task.user_id = data['user_id']

    if 'category_id' in data:
        if data['category_id'] and not Category.query.get(data['category_id']):
            raise ServiceError(404, 'Categoria não encontrada')
        task.category_id = data['category_id']

    if 'due_date' in data:
        if data['due_date']:
            task.due_date = _parse_due_date(data['due_date'], 'Formato de data inválido')
        else:
            task.due_date = None

    if 'tags' in data:
        task.tags = ','.join(data['tags']) if isinstance(data['tags'], list) else data['tags']

    task.updated_at = datetime.utcnow()

    try:
        db.session.commit()
        logger.info("Task atualizada: %s", task.id)
        return task.to_dict()
    except Exception as e:
        db.session.rollback()
        logger.error("Erro ao atualizar task: %s", e)
        raise ServiceError(500, 'Erro ao atualizar')


def delete_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        raise ServiceError(404, 'Task não encontrada')
    try:
        db.session.delete(task)
        db.session.commit()
        logger.info("Task deletada: %s", task_id)
    except Exception as e:
        db.session.rollback()
        logger.error("Erro ao deletar task: %s", e)
        raise ServiceError(500, 'Erro ao deletar')


def search_tasks(query, status, priority, user_id):
    q = Task.query
    if query:
        q = q.filter(db.or_(Task.title.like(f'%{query}%'), Task.description.like(f'%{query}%')))
    if status:
        q = q.filter(Task.status == status)
    if priority:
        q = q.filter(Task.priority == int(priority))
    if user_id:
        q = q.filter(Task.user_id == int(user_id))
    return [t.to_dict() for t in q.all()]


def stats():
    all_tasks = Task.query.all()
    total = len(all_tasks)
    counters = {s: 0 for s in VALID_STATUSES}
    overdue_count = 0
    for t in all_tasks:
        if t.status in counters:
            counters[t.status] += 1
        if t.is_overdue():
            overdue_count += 1
    return {
        'total': total,
        'pending': counters['pending'],
        'in_progress': counters['in_progress'],
        'done': counters['done'],
        'cancelled': counters['cancelled'],
        'overdue': overdue_count,
        'completion_rate': round((counters['done'] / total) * 100, 2) if total > 0 else 0,
    }
