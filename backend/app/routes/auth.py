from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
)
from app.services import (
    UserService,
    ProfessionalService,
    ValidationException,
    ServiceException,
)
from app.schemas.schema import UserSchema, CustomerSchema, ProfessionalSchema
from marshmallow import ValidationError
from datetime import datetime

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")
user_service = UserService()


@auth_bp.route("/login", methods=["POST"])
def login():
    """Authenticate user and return JWT tokens"""
    data = request.get_json()

    if not data or "email" not in data or "password" not in data:
        return jsonify({"error": "Email and password are required"}), 400

    # Check if login is for admin
    from flask import current_app

    if (
        data["email"] == current_app.config["ADMIN_EMAIL"]
        and data["password"] == current_app.config["ADMIN_PASSWORD"]
    ):
        # Create admin tokens
        access_token = create_access_token(
            identity=0,  # Admin ID is always 0
            additional_claims={
                "email": current_app.config["ADMIN_EMAIL"],
                "role": "ADMIN"
            }
        )
        refresh_token = create_refresh_token(identity=0)  # Admin ID is always 0

        return (
            jsonify(
                {
                    "access_token": access_token,
                    "refresh_token": refresh_token,

                    "email": current_app.config["ADMIN_EMAIL"],
                    "is_admin": True,
                    "user": {"role": "ADMIN"},
                    
                }
            ),
            200,
        )

    # Regular user authentication
    user = user_service.authenticate(data["email"], data["password"])

    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    # Prepare additional claims
    additional_claims = {
        "email": user.email,
        "role": user.role.value if hasattr(user, "role") else "customer"
    }
    
    # Add professional verification status if user is a professional
    if hasattr(user, "role") and user.role.value == "PROFESSIONAL" and hasattr(user, "professional"):
        additional_claims["is_verified"] = user.professional.is_verified
    
    # Create tokens
    access_token = create_access_token(
        identity=user.id,
        additional_claims=additional_claims
    )
    refresh_token = create_refresh_token(identity=user.id)

    # Prepare user data for response
    user_data = {"role": user.role.value if hasattr(user, "role") else "CUSTOMER"}
    
    # Add verification status for professionals
    if hasattr(user, "role") and user.role.value == "PROFESSIONAL" and hasattr(user, "professional"):
        user_data["is_verified"] = user.professional.is_verified
    
    return (
        jsonify(
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "email": user.email,
                "user": user_data,
            }
        ),
        200,
    )


@auth_bp.route("/register/customer", methods=["POST"])
def register_customer():
    """Register a new customer"""
    data = request.get_json()

    try:
        # Validate user data
        user_schema = UserSchema()
        user_data = user_schema.load(data)

        # Validate customer data
        customer_schema = CustomerSchema()
        customer_data = customer_schema.load(data)

        # Create user with customer role
        user_data["role"] = "CUSTOMER"
        user = user_service.create_user(user_data)

        # Create customer profile
        customer_data["user_id"] = user.id
        customer = user_service.create_customer(customer_data)

        # Generate tokens
        access_token = create_access_token(
            identity=user.id,
            additional_claims={"email": user.email, "role": "CUSTOMER"}
        )
        refresh_token = create_refresh_token(identity=user.id)

        return (
            jsonify(
                {
                    "message": "Customer registered successfully",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user_id": user.id,
                }
            ),
            201,
        )

    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except ValidationException as e:
        return jsonify({"error": e.message}), e.code
    except ServiceException as e:
        return jsonify({"error": e.message}), e.code


@auth_bp.route("/register/professional", methods=["POST"])
def register_professional():
    """Register a new professional"""

    professional_service = ProfessionalService()
    
    # Check if request has multipart form data (for document files)
    if request.content_type and 'multipart/form-data' in request.content_type:
        # Extract JSON data from form
        data = {}
        for key in request.form:
            data[key] = request.form[key]
    else:
        data = request.get_json()

    try:
        # Validate user data
        user_schema = UserSchema()
        user_data = user_schema.load(data)

        # Validate professional data
        professional_schema = ProfessionalSchema()
        professional_data = professional_schema.load(data)

        # Create professional with associated user
        professional = professional_service.create_professional(
            user_data, professional_data
        )
        user = professional.user

        # Handle document uploads if provided
        uploaded_documents = []
        if request.files and 'documents' in request.files:
            document_files = request.files.getlist('documents')
            
            if document_files and len(document_files) > 0:
                from app.services.professional_document_service import ProfessionalDocumentService
                document_service = ProfessionalDocumentService()
                
                document_type = data.get('document_type', 'identity_document')
                
                for file in document_files:
                    if file.filename == '':
                        continue
                        
                    document = document_service.save_document(
                        file=file,
                        professional_id=professional.id,
                        document_type=document_type
                    )
                    
                    uploaded_documents.append({
                        "id": document.id,
                        "document_type": document.document_type
                    })

        # Generate tokens
        access_token = create_access_token(
            identity=user.id,
            additional_claims={
                "email": user.email, 
                "role": "PROFESSIONAL",
                "is_verified": professional.is_verified
            }
        )
        refresh_token = create_refresh_token(identity=user.id)

        response_data = {
            "message": "Professional registered successfully",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user_id": user.id,
            "professional_id": professional.id,
        }
        
        # Add document info if any documents were uploaded
        if uploaded_documents:
            response_data["documents"] = uploaded_documents
            response_data["document_status"] = "pending_verification"

        return jsonify(response_data), 201

    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except ValidationException as e:
        return jsonify({"error": e.message}), e.code
    except ServiceException as e:
        return jsonify({"error": e.message}), e.code


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    current_user_id = get_jwt_identity()

    # Check if it's admin refresh
    if current_user_id == 0:  # Admin ID is always 0
        from flask import current_app

        # Create new admin access token
        access_token = create_access_token(
            identity=0,
            additional_claims={
                "email": current_app.config["ADMIN_EMAIL"],
                "role": "ADMIN"
            }
        )
        return jsonify({"access_token": access_token}), 200

    # Regular user refresh
    user = user_service.get_by_id(current_user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404
        
    # Prepare additional claims
    additional_claims = {
        "email": user.email,
        "role": user.role.value if hasattr(user, "role") else "customer"
    }
    
    # Add professional verification status if user is a professional
    if hasattr(user, "role") and user.role.value == "PROFESSIONAL" and hasattr(user, "professional"):
        additional_claims["is_verified"] = user.professional.is_verified

    # Create new access token
    access_token = create_access_token(
        identity=user.id,
        additional_claims=additional_claims
    )

    return jsonify({"access_token": access_token}), 200


@auth_bp.route("/change-password", methods=["POST"])
@jwt_required()
def change_password():
    """Change user password"""
    current_user = get_jwt_identity()
    data = request.get_json()

    if not data or "old_password" not in data or "new_password" not in data:
        return jsonify({"error": "Old password and new password are required"}), 400

    try:
        user_service.change_password(
            current_user["id"], data["old_password"], data["new_password"]
        )
        return jsonify({"message": "Password changed successfully"}), 200
    except ValidationException as e:
        return jsonify({"error": e.message}), e.code
    except ServiceException as e:
        return jsonify({"error": e.message}), e.code
