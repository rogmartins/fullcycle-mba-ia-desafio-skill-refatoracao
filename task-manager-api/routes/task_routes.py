from flask import Blueprint, request, jsonify
from database import db
from models.task import Task, VALID_STATUSES, MAX_TITLE_LENGTH, MIN_TITLE_LENGTH
from models.user import User
from models.category import Category
from datetime import datetime, timezone
from sqlalchemy.orm import joinedload

task_bp = Blueprint('tasks', __name__)


def _utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _parse_date(s):
    try:
        return datetime.strptime(s, '%Y-%m-%d')
    except (ValueError, TypeError):
        return None


@task_bp.route('/tasks', methods=['GET'])
def get_tasks():
    # REFACTORED: joinedload elimina N+1 queries para user e category (AP-08)
    tasks = Task.query.options(joinedload(Task.user), joinedload(Task.category)).all()
    result = []
    for t in tasks:
        data = t.to_dict()
        # REFACTORED: is_overdue() centralizado no modelo (AP-13)
        data['overdue'] = t.is_overdue()
        data['user_name'] = t.user.name if t.user else None
        data['category_name'] = t.category.name if t.category else None
        result.append(data)
    return jsonify(result), 200


@task_bp.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({'error': 'Task não encontrada'}), 404
    data = task.to_dict()
    data['overdue'] = task.is_overdue()
    return jsonify(data), 200


@task_bp.route('/tasks', methods=['POST'])
def create_task():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400

    title = data.get('title', '').strip()
    if not title:
        return jsonify({'error': 'Título é obrigatório'}), 400
    if len(title) < MIN_TITLE_LENGTH:
        return jsonify({'error': 'Título muito curto'}), 400
    if len(title) > MAX_TITLE_LENGTH:
        return jsonify({'error': 'Título muito longo'}), 400

    status = data.get('status', 'pending')
    if status not in VALID_STATUSES:
        return jsonify({'error': 'Status inválido'}), 400

    try:
        priority = int(data.get('priority', 3))
    except (TypeError, ValueError):
        return jsonify({'error': 'Prioridade inválida'}), 400
    if not 1 <= priority <= 5:
        return jsonify({'error': 'Prioridade deve ser entre 1 e 5'}), 400

    user_id = data.get('user_id')
    if user_id and not db.session.get(User, user_id):
        return jsonify({'error': 'Usuário não encontrado'}), 404

    category_id = data.get('category_id')
    if category_id and not db.session.get(Category, category_id):
        return jsonify({'error': 'Categoria não encontrada'}), 404

    task = Task(
        title=title,
        description=data.get('description', ''),
        status=status,
        priority=priority,
        user_id=user_id,
        category_id=category_id,
    )

    raw_due = data.get('due_date')
    if raw_due:
        parsed = _parse_date(raw_due)
        if not parsed:
            return jsonify({'error': 'Formato de data inválido. Use YYYY-MM-DD'}), 400
        task.due_date = parsed

    tags = data.get('tags')
    if tags:
        task.tags = ','.join(tags) if isinstance(tags, list) else tags

    try:
        db.session.add(task)
        db.session.commit()
        return jsonify(task.to_dict()), 201
    except Exception:
        db.session.rollback()
        return jsonify({'error': 'Erro ao criar task'}), 500


@task_bp.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({'error': 'Task não encontrada'}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400

    if 'title' in data:
        title = data['title'].strip()
        if len(title) < MIN_TITLE_LENGTH:
            return jsonify({'error': 'Título muito curto'}), 400
        if len(title) > MAX_TITLE_LENGTH:
            return jsonify({'error': 'Título muito longo'}), 400
        task.title = title

    if 'description' in data:
        task.description = data['description']

    if 'status' in data:
        if data['status'] not in VALID_STATUSES:
            return jsonify({'error': 'Status inválido'}), 400
        task.status = data['status']

    if 'priority' in data:
        try:
            p = int(data['priority'])
        except (TypeError, ValueError):
            return jsonify({'error': 'Prioridade inválida'}), 400
        if not 1 <= p <= 5:
            return jsonify({'error': 'Prioridade deve ser entre 1 e 5'}), 400
        task.priority = p

    if 'user_id' in data:
        if data['user_id'] and not db.session.get(User, data['user_id']):
            return jsonify({'error': 'Usuário não encontrado'}), 404
        task.user_id = data['user_id']

    if 'category_id' in data:
        if data['category_id'] and not db.session.get(Category, data['category_id']):
            return jsonify({'error': 'Categoria não encontrada'}), 404
        task.category_id = data['category_id']

    if 'due_date' in data:
        if data['due_date']:
            parsed = _parse_date(data['due_date'])
            if not parsed:
                return jsonify({'error': 'Formato de data inválido'}), 400
            task.due_date = parsed
        else:
            task.due_date = None

    if 'tags' in data:
        tags = data['tags']
        task.tags = ','.join(tags) if isinstance(tags, list) else tags

    task.updated_at = _utcnow()

    try:
        db.session.commit()
        return jsonify(task.to_dict()), 200
    except Exception:
        db.session.rollback()
        return jsonify({'error': 'Erro ao atualizar'}), 500


@task_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({'error': 'Task não encontrada'}), 404
    try:
        db.session.delete(task)
        db.session.commit()
        return jsonify({'message': 'Task deletada com sucesso'}), 200
    except Exception:
        db.session.rollback()
        return jsonify({'error': 'Erro ao deletar'}), 500


@task_bp.route('/tasks/search', methods=['GET'])
def search_tasks():
    q = request.args.get('q', '')
    status = request.args.get('status', '')
    priority = request.args.get('priority', '')
    user_id = request.args.get('user_id', '')

    query = Task.query
    if q:
        query = query.filter(db.or_(Task.title.like(f'%{q}%'), Task.description.like(f'%{q}%')))
    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == int(priority))
    if user_id:
        query = query.filter(Task.user_id == int(user_id))

    return jsonify([t.to_dict() for t in query.all()]), 200


@task_bp.route('/tasks/stats', methods=['GET'])
def task_stats():
    total = Task.query.count()
    done = Task.query.filter_by(status='done').count()
    # REFACTORED: is_overdue() centralizado no modelo; contagem via query (AP-13)
    all_tasks = Task.query.all()
    overdue_count = sum(1 for t in all_tasks if t.is_overdue())

    return jsonify({
        'total': total,
        'pending': Task.query.filter_by(status='pending').count(),
        'in_progress': Task.query.filter_by(status='in_progress').count(),
        'done': done,
        'cancelled': Task.query.filter_by(status='cancelled').count(),
        'overdue': overdue_count,
        'completion_rate': round((done / total) * 100, 2) if total > 0 else 0,
    }), 200
