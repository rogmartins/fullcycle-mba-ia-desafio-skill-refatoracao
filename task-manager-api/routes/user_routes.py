# REFACTORED: [HIGH] Controller fino — delega regra ao user_service.
from flask import Blueprint, request, jsonify

from services import user_service
from services.errors import ServiceError

user_bp = Blueprint('users', __name__)


@user_bp.route('/users', methods=['GET'])
def get_users():
    return jsonify(user_service.list_users()), 200


@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        return jsonify(user_service.get_user(user_id)), 200
    except ServiceError as e:
        return jsonify({'error': e.message}), e.status


@user_bp.route('/users', methods=['POST'])
def create_user():
    try:
        return jsonify(user_service.create_user(request.get_json())), 201
    except ServiceError as e:
        return jsonify({'error': e.message}), e.status


@user_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        return jsonify(user_service.update_user(user_id, request.get_json())), 200
    except ServiceError as e:
        return jsonify({'error': e.message}), e.status


@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        user_service.delete_user(user_id)
        return jsonify({'message': 'Usuário deletado com sucesso'}), 200
    except ServiceError as e:
        return jsonify({'error': e.message}), e.status


@user_bp.route('/users/<int:user_id>/tasks', methods=['GET'])
def get_user_tasks(user_id):
    try:
        return jsonify(user_service.get_user_tasks(user_id)), 200
    except ServiceError as e:
        return jsonify({'error': e.message}), e.status


@user_bp.route('/login', methods=['POST'])
def login():
    try:
        return jsonify(user_service.login(request.get_json())), 200
    except ServiceError as e:
        return jsonify({'error': e.message}), e.status
