from flask import Blueprint, request, jsonify
from models.user import User
from routes.auth_routes import auth_required
from pymongo.errors import DuplicateKeyError

# Create a Blueprint
user_bp = Blueprint('user', __name__, url_prefix='/api/users')


@user_bp.route('/', methods=['POST'])
@auth_required
def create_user():
    # (Your create_user logic from app.py goes here, with minor modifications)
    data = request.get_json()

    try:
        user = User(**data)
        user_id = user.save()
        if user_id:
            return jsonify({"id": str(user_id)}), 201  # Created
        else:
            return jsonify({"error": "User already exists"}), 409  # Conflict
    except KeyError as e:
        # Bad Request
        return jsonify({"error": f"Missing field: {e.args[0]}"}), 400


@user_bp.route('/')
@auth_required
def get_users():
    from models.user import User

    username = request.args.get('username')
    users = User.find(username=username)
    return jsonify([user.to_dict() for user in users]), 200


@user_bp.route('/<username>', methods=['PUT'])
@auth_required
def update_user(username):
    from models.user import User

    data = request.get_json()
    users = User.find(username=username)

    if users:
        user = users[0]  # Get the first (and hopefully only) user object
        # Call the update method on the User instance
        modified_count = user.update(data)
        if modified_count > 0:
            return jsonify({"message": "User updated successfully"}), 200
        else:
            # Internal Server Error
            return jsonify({"error": "User not updated"}), 500
    else:
        return jsonify({"error": "User not found"}), 404  # Not Found


@user_bp.route('/<username>', methods=['DELETE'])
@auth_required
def delete_user(username):
    from models.user import User

    if User.delete(username):
        return '', 204  # No Content (successful delete)
    else:
        return jsonify({"error": "User not found"}), 404  # Not Found
