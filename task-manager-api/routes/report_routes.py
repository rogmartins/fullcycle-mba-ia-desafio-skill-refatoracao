from flask import Blueprint, request, jsonify
from database import db
from models.task import Task
from models.user import User
from models.category import Category
from sqlalchemy.orm import joinedload
# REFACTORED: lógica de relatório delegada ao ReportService — rota só orquestra
from services import report_service

report_bp = Blueprint('reports', __name__)

@report_bp.route('/reports/summary', methods=['GET'])
def summary_report():
    report = report_service.get_summary()
    return jsonify(report), 200

@report_bp.route('/reports/user/<int:user_id>', methods=['GET'])
def user_report(user_id):
    user = User.query.options(joinedload(User.tasks)).filter_by(id=user_id).first()
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404

    report = report_service.get_user_report(user)
    return jsonify(report), 200

@report_bp.route('/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    result = []
    for c in categories:
        cat_data = c.to_dict()
        cat_data['task_count'] = Task.query.filter_by(category_id=c.id).count()
        result.append(cat_data)
    return jsonify(result), 200

@report_bp.route('/categories', methods=['POST'])
def create_category():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Dados inválidos'}), 400

    name = data.get('name')
    if not name:
        return jsonify({'error': 'Nome é obrigatório'}), 400

    category = Category()
    category.name = name
    category.description = data.get('description', '')
    category.color = data.get('color', '#000000')

    try:
        db.session.add(category)
        db.session.commit()
        return jsonify(category.to_dict()), 201
    except:
        db.session.rollback()
        return jsonify({'error': 'Erro ao criar categoria'}), 500

@report_bp.route('/categories/<int:cat_id>', methods=['PUT'])
def update_category(cat_id):
    cat = Category.query.get(cat_id)
    if not cat:
        return jsonify({'error': 'Categoria não encontrada'}), 404

    data = request.get_json()
    if 'name' in data:
        cat.name = data['name']
    if 'description' in data:
        cat.description = data['description']
    if 'color' in data:
        cat.color = data['color']

    try:
        db.session.commit()
        return jsonify(cat.to_dict()), 200
    except:
        db.session.rollback()
        return jsonify({'error': 'Erro ao atualizar'}), 500

@report_bp.route('/categories/<int:cat_id>', methods=['DELETE'])
def delete_category(cat_id):
    cat = Category.query.get(cat_id)
    if not cat:
        return jsonify({'error': 'Categoria não encontrada'}), 404

    try:
        db.session.delete(cat)
        db.session.commit()
        return jsonify({'message': 'Categoria deletada'}), 200
    except:
        db.session.rollback()
        return jsonify({'error': 'Erro ao deletar'}), 500
