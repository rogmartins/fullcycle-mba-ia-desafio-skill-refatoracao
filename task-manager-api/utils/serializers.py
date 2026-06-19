# REFACTORED: [MEDIUM] Serialização centralizada (antes dicts montados à mão e duplicados nas rotas).


def serialize_task_list_item(task):
    """Task com overdue + nome do usuário/categoria (formato de GET /tasks)."""
    data = task.to_dict()
    data['overdue'] = task.is_overdue()
    data['user_name'] = task.user.name if task.user else None
    data['category_name'] = task.category.name if task.category else None
    return data


def serialize_task_detail(task):
    """Task completa + overdue (formato de GET /tasks/<id>)."""
    data = task.to_dict()
    data['overdue'] = task.is_overdue()
    return data


def serialize_user_task_item(task):
    """Subconjunto usado em GET /users/<id>/tasks."""
    return {
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'status': task.status,
        'priority': task.priority,
        'created_at': str(task.created_at),
        'due_date': str(task.due_date) if task.due_date else None,
        'overdue': task.is_overdue(),
    }
