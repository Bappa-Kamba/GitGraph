# repository_routes.py

from flask import Blueprint, request, jsonify
from models.repository import Repository
from pymongo.errors import DuplicateKeyError

repository_bp = Blueprint('repository', __name__,
                          url_prefix='/api/repositories')


@repository_bp.route('/', methods=['POST'])
def create_repository():

    data = request.get_json()

    if not all(key in data for key in ('name', 'owner', 'description', 'url')):
        return jsonify({"error": "Missing required fields"}), 400

    if not isinstance(data["name"], str) or not isinstance(data["owner"], str) or not isinstance(data["description"], str) or not isinstance(data["url"], str):
        return jsonify({"error": "Invalid data type for name, owner, description or url"}), 400

    try:
        repo = Repository.create(**data)
        if repo:
            return jsonify(repo.to_dict()), 201  # Created
        else:
            # Conflict
            return jsonify({"error": "Repository already exists"}), 409
    except DuplicateKeyError:
        return jsonify({"error": "Repository already exists"}), 409  # Conflict


@repository_bp.route('/', methods=['GET'])
def get_repositories():

    owner = request.args.get('owner')
    name = request.args.get('name')

    query = {}
    if owner:
        query["owner"] = owner
    if name:
        query["name"] = name

    repositories = Repository.find(**query)
    return jsonify([repo.to_dict() for repo in repositories]), 200


@repository_bp.route('/<name>', methods=['PUT'])
def update_repository(name):
    data = request.get_json()
    repos = Repository.find(name=name)

    if repos:
        repo = repos[0]
        if repo.update(data):
            return jsonify({"message": "Repository updated successfully"}), 200
        else:
            return jsonify({"error": "Repository not updated"}), 500
    else:
        return jsonify({"error": "Repository not found"}), 404


@repository_bp.route('/<name>', methods=['DELETE'])
def delete_repository(name):

    if Repository.delete(name):
        return '', 204  # No Content (successful delete)
    else:
        return jsonify({"error": "User not found"}), 404  # Not Found
