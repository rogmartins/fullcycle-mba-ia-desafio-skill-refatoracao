from flask import Blueprint, request, jsonify
from database import db
from models.task import Task
from models.user import User
from models.category import Category
from datetime import datetime, timezone, timedelta
from sqlalchemy import func

report_bp = Blueprint('reports', __name__)

# REFACTORED: utcnow() depreciado substituído por datetime.now(timezone.utc) (AP-10)
def _utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


@report_bp.route('/reports/summary', methods=['GET'])
def summary_report():
    total_tasks = Task.query.count()
    total_users = User.query.count()
    total_categories = Category.query.count()

    pending = Task.query.filter_by(status='pending').count()
    in_progress = Task.query.filter_by(status='in_progress').count()
    done = Task.query.filter_by(status='done').count()
    cancelled = Task.query.filter_by(status='cancelled').count()

    p1 = Task.query.filter_by(priority=1).count()
    p2 = Task.query.filter_by(priority=2).count()
    p3 = Task.query.filter_by(priority=3).count()
    p4 = Task.query.filter_by(priority=4).count()
    p5 = Task.query.filter_by(priority=5).count()

    all_tasks = Task.query.all()
    overdue_count = 0
    overdue_list = []
    now = _utcnow()
    for t in all_tasks:
        # REFACTORED: is_overdue() centralizado no modelo (AP-13)
        if t.is_overdue():
            overdue_count += 1
            overdue_list.append({
                'id': t.id,
                'title': t.title,
                'due_date': str(t.due_date),
                'days_overdue': (now - t.due_date).days
            })

    seven_days_ago = now - timedelta(days=7)
    recent_tasks = Task.query.filter(Task.created_at >= seven_days_ago).count()
    recent_done = Task.query.filter(Task.status == 'done', Task.updated_at >= seven_days_ago).count()

    # REFACTORED: N+1 eliminado — query única com JOIN e GROUP BY (AP-08)
    user_stats_q = db.session.query(
        User.id,
        User.name,
        func.count(Task.id).label('total'),
        func.sum(db.case((Task.status == 'done', 1), else_=0)).label('completed')
    ).outerjoin(Task, Task.user_id == User.id).group_by(User.id, User.name).all()

    user_stats = [{
        'user_id': row.id,
        'user_name': row.name,
        'total_tasks': row.total or 0,
        'completed_tasks': int(row.completed or 0),
        'completion_rate': round((int(row.completed or 0) / row.total) * 100, 2) if row.total else 0
    } for row in user_stats_q]

    return jsonify({
        'generated_at': str(now),
        'overview': {
            'total_tasks': total_tasks,
            'total_users': total_users,
            'total_categories': total_categories,
        },
        'tasks_by_status': {
            'pending': pending,
            'in_progress': in_progress,
            'done': done,
            'cancelled': cancelled,
        },
        'tasks_by_priority': {
            'critical': p1,
            'high': p2,
            'medium': p3,
            'low': p4,
            'minimal': p5,
        },
        'overdue': {
            'count': overdue_count,
            'tasks': overdue_list,
        },
        'recent_activity': {
            'tasks_created_last_7_days': recent_tasks,
            'tasks_completed_last_7_days': recent_done,
        },
        'user_productivity': user_stats,
    }), 200


@report_bp.route('/reports/user/<int:user_id>', methods=['GET'])
def user_report(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404

    tasks = Task.query.filter_by(user_id=user_id).all()
    total = len(tasks)
    done = pending = in_progress = cancelled = overdue = high_priority = 0

    for t in tasks:
        if t.status == 'done':
            done += 1
        elif t.status == 'pending':
            pending += 1
        elif t.status == 'in_progress':
            in_progress += 1
        elif t.status == 'cancelled':
            cancelled += 1
        if t.priority <= 2:
            high_priority += 1
        # REFACTORED: is_overdue() centralizado no modelo (AP-13)
        if t.is_overdue():
            overdue += 1

    return jsonify({
        'user': {'id': user.id, 'name': user.name, 'email': user.email},
        'statistics': {
            'total_tasks': total,
            'done': done,
            'pending': pending,
            'in_progress': in_progress,
            'cancelled': cancelled,
            'overdue': overdue,
            'high_priority': high_priority,
            'completion_rate': round((done / total) * 100, 2) if total > 0 else 0,
        }
    }), 200
