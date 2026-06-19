# REFACTORED: [HIGH] Controller fino — delega regra/serialização ao task_service.
import logging

from flask import Blueprint, request, jsonify

from services import task_service
from services.errors import ServiceError

logger = logging.getLogger(__name__)
task_bp = Blueprint('tasks', __name__)


@task_bp.route('/tasks', methods=['GET'])
def get_tasks():
    try:
        return jsonify(task_service.list_tasks()), 200
    except Exception as e:
        logger.error("Erro ao listar tasks: %s", e)
        return jsonify({'error': 'Erro interno'}), 500


@task_bp.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    try:
        return jsonify(task_service.get_task(task_id)), 200
    except ServiceError as e:
        return jsonify({'error': e.message}), e.status


@task_bp.route('/tasks', methods=['POST'])
def create_task():
    try:
        return jsonify(task_service.create_task(request.get_json())), 201
    except ServiceError as e:
        return jsonify({'error': e.message}), e.status


@task_bp.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    try:
        return jsonify(task_service.update_task(task_id, request.get_json())), 200
    except ServiceError as e:
        return jsonify({'error': e.message}), e.status


@task_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    try:
        task_service.delete_task(task_id)
        return jsonify({'message': 'Task deletada com sucesso'}), 200
    except ServiceError as e:
        return jsonify({'error': e.message}), e.status


@task_bp.route('/tasks/search', methods=['GET'])
def search_tasks():
    results = task_service.search_tasks(
        request.args.get('q', ''),
        request.args.get('status', ''),
        request.args.get('priority', ''),
        request.args.get('user_id', ''),
    )
    return jsonify(results), 200


@task_bp.route('/tasks/stats', methods=['GET'])
def task_stats():
    return jsonify(task_service.stats()), 200
