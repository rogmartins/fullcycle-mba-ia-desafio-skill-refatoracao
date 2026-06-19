# REFACTORED: [HIGH] Relatórios isolados em serviço, sem N+1 por usuário.
from datetime import datetime, timedelta

from models.task import Task
from models.user import User
from models.category import Category
from constants import TERMINAL_STATUSES
from services.errors import ServiceError


def summary():
    all_tasks = Task.query.all()
    total_tasks = len(all_tasks)
    total_users = User.query.count()
    total_categories = Category.query.count()

    by_status = {'pending': 0, 'in_progress': 0, 'done': 0, 'cancelled': 0}
    by_priority = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    overdue_list = []
    now = datetime.utcnow()
    for t in all_tasks:
        if t.status in by_status:
            by_status[t.status] += 1
        if t.priority in by_priority:
            by_priority[t.priority] += 1
        if t.due_date and t.due_date < now and t.status not in TERMINAL_STATUSES:
            overdue_list.append({
                'id': t.id,
                'title': t.title,
                'due_date': str(t.due_date),
                'days_overdue': (now - t.due_date).days,
            })

    seven_days_ago = now - timedelta(days=7)
    recent_tasks = sum(1 for t in all_tasks if t.created_at and t.created_at >= seven_days_ago)
    recent_done = sum(
        1 for t in all_tasks
        if t.status == 'done' and t.updated_at and t.updated_at >= seven_days_ago
    )

    # REFACTORED: [HIGH] Agrupa tasks por usuário em memória (antes 1 query por usuário).
    tasks_by_user = {}
    for t in all_tasks:
        tasks_by_user.setdefault(t.user_id, []).append(t)

    user_stats = []
    for u in User.query.all():
        u_tasks = tasks_by_user.get(u.id, [])
        total = len(u_tasks)
        completed = sum(1 for t in u_tasks if t.status == 'done')
        user_stats.append({
            'user_id': u.id,
            'user_name': u.name,
            'total_tasks': total,
            'completed_tasks': completed,
            'completion_rate': round((completed / total) * 100, 2) if total > 0 else 0,
        })

    return {
        'generated_at': str(now),
        'overview': {
            'total_tasks': total_tasks,
            'total_users': total_users,
            'total_categories': total_categories,
        },
        'tasks_by_status': by_status,
        'tasks_by_priority': {
            'critical': by_priority[1],
            'high': by_priority[2],
            'medium': by_priority[3],
            'low': by_priority[4],
            'minimal': by_priority[5],
        },
        'overdue': {'count': len(overdue_list), 'tasks': overdue_list},
        'recent_activity': {
            'tasks_created_last_7_days': recent_tasks,
            'tasks_completed_last_7_days': recent_done,
        },
        'user_productivity': user_stats,
    }


def user_report(user_id):
    user = User.query.get(user_id)
    if not user:
        raise ServiceError(404, 'Usuário não encontrado')

    tasks = Task.query.filter_by(user_id=user_id).all()
    total = len(tasks)
    counters = {'done': 0, 'pending': 0, 'in_progress': 0, 'cancelled': 0}
    overdue = 0
    high_priority = 0
    now = datetime.utcnow()
    for t in tasks:
        if t.status in counters:
            counters[t.status] += 1
        if t.priority <= 2:
            high_priority += 1
        if t.due_date and t.due_date < now and t.status not in TERMINAL_STATUSES:
            overdue += 1

    return {
        'user': {'id': user.id, 'name': user.name, 'email': user.email},
        'statistics': {
            'total_tasks': total,
            'done': counters['done'],
            'pending': counters['pending'],
            'in_progress': counters['in_progress'],
            'cancelled': counters['cancelled'],
            'overdue': overdue,
            'high_priority': high_priority,
            'completion_rate': round((counters['done'] / total) * 100, 2) if total > 0 else 0,
        },
    }
