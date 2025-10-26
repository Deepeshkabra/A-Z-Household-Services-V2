from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services import (
    UserService,
    ValidationException,
    ServiceException,
    ResourceNotFoundException,
)
from app.schemas.schema import UserSchema
from marshmallow import ValidationError

user_bp = Blueprint("user", __name__, url_prefix="/api/users")
user_service = UserService()


@user_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    """Get current user profile"""
    current_user_id = get_jwt_identity()

    try:
        user = user_service.get_or_404(current_user_id)
        user_schema = UserSchema()
        return jsonify(user_schema.dump(user)), 200
    except ResourceNotFoundException as e:
        return jsonify({"error": e.message}), e.code
    except ServiceException as e:
        return jsonify({"error": e.message}), e.code


@user_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    """Update current user profile"""
    current_user_id = get_jwt_identity()
    data = request.get_json()

    try:
        # Validate update data
        user_schema = UserSchema(partial=True)
        profile_data = user_schema.load(data)

        # Remove password from update data if present
        if "password" in profile_data:
            del profile_data["password"]

        # Update user profile
        updated_user = user_service.update_profile(current_user_id, profile_data)

        return (
            jsonify(
                {
                    "message": "Profile updated successfully",
                    "user": user_schema.dump(updated_user),
                }
            ),
            200,
        )
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except ValidationException as e:
        return jsonify({"error": e.message}), e.code
    except ResourceNotFoundException as e:
        return jsonify({"error": e.message}), e.code
    except ServiceException as e:
        return jsonify({"error": e.message}), e.code


@user_bp.route("/<int:user_id>", methods=["GET"])
@jwt_required()
def get_user(user_id):
    """Get user by ID (admin only)"""
    current_user_id = get_jwt_identity()
    from flask_jwt_extended import get_jwt
    jwt_data = get_jwt()

    # Check if user is admin
    if "role" not in jwt_data or jwt_data["role"] != "admin":
        return jsonify({"error": "Unauthorized access"}), 403

    try:
        user = user_service.get_or_404(user_id)
        user_schema = UserSchema()
        return jsonify(user_schema.dump(user)), 200
    except ResourceNotFoundException as e:
        return jsonify({"error": e.message}), e.code
    except ServiceException as e:
        return jsonify({"error": e.message}), e.code


@user_bp.route("/deactivate", methods=["POST"])
@jwt_required()
def deactivate_account():
    """Deactivate current user account"""
    current_user_id = get_jwt_identity()

    try:
        user_service.update(current_user_id, is_active=False)
        return jsonify({"message": "Account deactivated successfully"}), 200
    except ResourceNotFoundException as e:
        return jsonify({"error": e.message}), e.code
    except ServiceException as e:
        return jsonify({"error": e.message}), e.code
