# REFACTORED: [HIGH/LOW] Controller fino; imports não usados removidos.
from flask import Blueprint, request, jsonify

from services import report_service, category_service
from services.errors import ServiceError

report_bp = Blueprint('reports', __name__)


@report_bp.route('/reports/summary', methods=['GET'])
def summary_report():
    return jsonify(report_service.summary()), 200


@report_bp.route('/reports/user/<int:user_id>', methods=['GET'])
def user_report(user_id):
    try:
        return jsonify(report_service.user_report(user_id)), 200
    except ServiceError as e:
        return jsonify({'error': e.message}), e.status


@report_bp.route('/categories', methods=['GET'])
def get_categories():
    return jsonify(category_service.list_categories()), 200


@report_bp.route('/categories', methods=['POST'])
def create_category():
    try:
        return jsonify(category_service.create_category(request.get_json())), 201
    except ServiceError as e:
        return jsonify({'error': e.message}), e.status


@report_bp.route('/categories/<int:cat_id>', methods=['PUT'])
def update_category(cat_id):
    try:
        return jsonify(category_service.update_category(cat_id, request.get_json())), 200
    except ServiceError as e:
        return jsonify({'error': e.message}), e.status


@report_bp.route('/categories/<int:cat_id>', methods=['DELETE'])
def delete_category(cat_id):
    try:
        category_service.delete_category(cat_id)
        return jsonify({'message': 'Categoria deletada'}), 200
    except ServiceError as e:
        return jsonify({'error': e.message}), e.status
