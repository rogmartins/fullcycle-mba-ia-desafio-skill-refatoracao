# REFACTORED: [HIGH] Regra de negócio de categorias fora das rotas.
import logging

from database import db
from models.category import Category
from models.task import Task
from services.errors import ServiceError

logger = logging.getLogger(__name__)


def list_categories():
    # REFACTORED: contagem de tasks por categoria em uma única consulta agrupada (evita N+1).
    counts = dict(
        db.session.query(Task.category_id, db.func.count(Task.id))
        .group_by(Task.category_id)
        .all()
    )
    result = []
    for c in Category.query.all():
        data = c.to_dict()
        data['task_count'] = counts.get(c.id, 0)
        result.append(data)
    return result


def create_category(data):
    if not data:
        raise ServiceError(400, 'Dados inválidos')
    name = data.get('name')
    if not name:
        raise ServiceError(400, 'Nome é obrigatório')

    category = Category()
    category.name = name
    category.description = data.get('description', '')
    category.color = data.get('color', '#000000')

    try:
        db.session.add(category)
        db.session.commit()
        return category.to_dict()
    except Exception as e:
        db.session.rollback()
        logger.error("Erro ao criar categoria: %s", e)
        raise ServiceError(500, 'Erro ao criar categoria')


def update_category(cat_id, data):
    cat = Category.query.get(cat_id)
    if not cat:
        raise ServiceError(404, 'Categoria não encontrada')

    if 'name' in data:
        cat.name = data['name']
    if 'description' in data:
        cat.description = data['description']
    if 'color' in data:
        cat.color = data['color']

    try:
        db.session.commit()
        return cat.to_dict()
    except Exception as e:
        db.session.rollback()
        logger.error("Erro ao atualizar categoria: %s", e)
        raise ServiceError(500, 'Erro ao atualizar')


def delete_category(cat_id):
    cat = Category.query.get(cat_id)
    if not cat:
        raise ServiceError(404, 'Categoria não encontrada')
    try:
        db.session.delete(cat)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error("Erro ao deletar categoria: %s", e)
        raise ServiceError(500, 'Erro ao deletar')
