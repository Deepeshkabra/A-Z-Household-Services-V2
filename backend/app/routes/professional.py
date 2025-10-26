from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services import (
    ProfessionalService,
    ValidationException,
    ServiceException,
    ResourceNotFoundException,
)
from app.schemas.schema import ProfessionalSchema, UserSchema
from marshmallow import ValidationError

professional_bp = Blueprint("professional", __name__, url_prefix="/api/professionals")
professional_service = ProfessionalService()


@professional_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    """Get current professional profile"""
    current_user = get_jwt_identity()

    try:
        # Get professional by user ID
        professional = professional_service.get_by_user_id(current_user["id"])
        if not professional:
            return jsonify({"error": "Professional profile not found"}), 404

        professional_schema = ProfessionalSchema()
        return jsonify(professional_schema.dump(professional)), 200
    except ServiceException as e:
        return jsonify({"error": e.message}), e.code


@professional_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    """Update professional profile"""
    current_user = get_jwt_identity()
    data = request.get_json()

    try:
        # Get professional by user ID
        professional = professional_service.get_by_user_id(current_user["id"])
        if not professional:
            return jsonify({"error": "Professional profile not found"}), 404

        # Validate update data
        professional_schema = ProfessionalSchema(partial=True)
        profile_data = professional_schema.load(data)

        # Update professional profile
        updated_professional = professional_service.update(
            professional.id, **profile_data
        )

        return (
            jsonify(
                {
                    "message": "Profile updated successfully",
                    "professional": professional_schema.dump(updated_professional),
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


@professional_bp.route("/<int:professional_id>", methods=["GET"])
@jwt_required()
def get_professional(professional_id):
    """Get professional by ID"""
    try:
        professional = professional_service.get_or_404(professional_id)
        professional_schema = ProfessionalSchema()
        return jsonify(professional_schema.dump(professional)), 200
    except ResourceNotFoundException as e:
        return jsonify({"error": e.message}), e.code
    except ServiceException as e:
        return jsonify({"error": e.message}), e.code


@professional_bp.route("/service/<int:service_id>", methods=["GET"])
def get_professionals_by_service(service_id):
    """Get professionals by service ID"""
    pincode = request.args.get("pincode")

    if not pincode:
        return jsonify({"error": "Pincode is required"}), 400

    try:
        professionals = professional_service.get_available_professionals(
            service_id, pincode
        )
        professional_schema = ProfessionalSchema(many=True)
        return jsonify(professional_schema.dump(professionals)), 200
    except ValidationException as e:
        return jsonify({"error": e.message}), e.code
    except ServiceException as e:
        return jsonify({"error": e.message}), e.code


@professional_bp.route("/documents", methods=["POST"])
@jwt_required()
def upload_documents():
    """Upload professional documents for verification"""
    current_user = get_jwt_identity()

    try:
        # Get professional by user ID
        professional = professional_service.get_by_user_id(current_user["id"])
        if not professional:
            return jsonify({"error": "Professional profile not found"}), 404

        # Check if documents were uploaded
        if 'documents' not in request.files:
            return jsonify({"error": "No document files provided"}), 400

        from app.services.professional_document_service import ProfessionalDocumentService
        document_service = ProfessionalDocumentService()
        
        uploaded_documents = []
        document_files = request.files.getlist('documents')
        
        if not document_files or len(document_files) == 0:
            return jsonify({"error": "No document files provided"}), 400
            
        # Get document type from form data
        document_type = request.form.get('document_type', 'identity_document')
        
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
                "document_type": document.document_type,
                "is_verified": document.is_verified
            })
        
        if not uploaded_documents:
            return jsonify({"error": "No valid documents were uploaded"}), 400
            
        return (
            jsonify(
                {
                    "message": f"{len(uploaded_documents)} document(s) uploaded successfully",
                    "status": "pending_verification",
                    "documents": uploaded_documents
                }
            ),
            200,
        )
    except ValidationException as e:
        return jsonify({"error": e.message}), e.code
    except ServiceException as e:
        return jsonify({"error": e.message}), e.code
