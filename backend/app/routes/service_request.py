from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services import (
    ServiceRequestService,
    ValidationException,
    ServiceException,
    ResourceNotFoundException,
)
from app.schemas.schema import ServiceRequestSchema, ReviewSchema
from marshmallow import ValidationError

service_request_bp = Blueprint(
    "service_request", __name__, url_prefix="/api/service-requests"
)
service_request_service = ServiceRequestService()


@service_request_bp.route("", methods=["POST"])
@jwt_required()
def create_service_request():
    """Create a new service request"""
    current_user = get_jwt_identity()
    data = request.get_json()

    try:
        # Validate request data
        service_request_schema = ServiceRequestSchema()
        request_data = service_request_schema.load(data)

        # Create service request
        service_request = service_request_service.create_request(
            customer_id=current_user, **request_data
        )

        return (
            jsonify(
                {
                    "message": "Service request created successfully",
                    "service_request": service_request_schema.dump(service_request),
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


@service_request_bp.route("/<int:request_id>", methods=["GET"])
@jwt_required()
def get_service_request(request_id):
    """Get service request by ID"""
    current_user = get_jwt_identity()

    try:
        service_request = service_request_service.get_or_404(request_id)

        # Check if user is authorized to view this request
        if (
            service_request.customer_id != current_user["id"]
            and (
                not hasattr(service_request, "professional_id")
                or service_request.professional_id != current_user["id"]
            )
            and current_user.get("role") != "admin"
        ):
            return jsonify({"error": "Unauthorized access"}), 403

        service_request_schema = ServiceRequestSchema()
        return jsonify(service_request_schema.dump(service_request)), 200
    except ResourceNotFoundException as e:
        return jsonify({"error": e.message}), e.code
    except ServiceException as e:
        return jsonify({"error": e.message}), e.code


@service_request_bp.route("/customer", methods=["GET"])
@jwt_required()
def get_customer_requests():
    """Get all service requests for current customer"""
    current_user = get_jwt_identity()

    try:
        # Get all requests for the customer
        service_requests = service_request_service.get_by_customer_id(
            current_user
        )
        service_request_schema = ServiceRequestSchema(many=True)
        return jsonify(service_request_schema.dump(service_requests)), 200
    except ServiceException as e:
        return jsonify({"error": e.message}), e.code


@service_request_bp.route("/professional", methods=["GET"])
@jwt_required()
def get_professional_requests():
    """Get all service requests for current professional"""
    current_user = get_jwt_identity()

    try:
        # Get all requests for the professional
        service_requests = service_request_service.get_by_professional_id(
            current_user
        )
        service_request_schema = ServiceRequestSchema(many=True)
        return jsonify(service_request_schema.dump(service_requests)), 200
    except ServiceException as e:
        return jsonify({"error": e.message}), e.code


@service_request_bp.route("/available", methods=["GET"])
@jwt_required()
def get_available_requests():
    """Get all available service requests for current professional's service type"""
    current_user = get_jwt_identity()
    
    # Check if user is a professional
    from flask_jwt_extended import get_jwt
    jwt_data = get_jwt()
    
    if jwt_data.get("role") != "PROFESSIONAL":
        return jsonify({"error": "Only professionals can view available requests"}), 403

    try:
        # Get professional's service ID
        from app.services import ProfessionalService
        professional_service = ProfessionalService()
        professional = professional_service.get_by_user_id(current_user)
        
        if not professional:
            return jsonify({"error": "Professional profile not found"}), 404
            
        if not professional.is_verified:
            return jsonify({"error": "Your account must be verified to view available requests"}), 403

        # Get available requests for the professional's service type
        service_requests = service_request_service.get_available_requests_by_service(
            professional.service_id
        )
        service_request_schema = ServiceRequestSchema(many=True)
        return jsonify(service_request_schema.dump(service_requests)), 200
    except ServiceException as e:
        return jsonify({"error": e.message}), e.code


@service_request_bp.route("/<int:request_id>/assign", methods=["POST"])
@jwt_required()
def assign_professional(request_id):
    """Assign a professional to a service request (admin only)"""
    current_user = get_jwt_identity()
    data = request.get_json()

    # Check if user is admin
    if current_user.get("role") != "admin":
        return jsonify({"error": "Unauthorized access"}), 403

    if not data or "professional_id" not in data:
        return jsonify({"error": "Professional ID is required"}), 400

    try:
        service_request = service_request_service.assign_professional(
            request_id=request_id, professional_id=data["professional_id"]
        )

        service_request_schema = ServiceRequestSchema()
        return (
            jsonify(
                {
                    "message": "Professional assigned successfully",
                    "service_request": service_request_schema.dump(service_request),
                }
            ),
            200,
        )
    except ValidationException as e:
        return jsonify({"error": e.message}), e.code
    except ResourceNotFoundException as e:
        return jsonify({"error": e.message}), e.code
    except ServiceException as e:
        return jsonify({"error": e.message}), e.code


@service_request_bp.route("/<int:request_id>/complete", methods=["POST"])
@jwt_required()
def complete_service(request_id):
    """Complete a service request and add review"""
    current_user = get_jwt_identity()
    data = request.get_json()

    try:
        # Get the service request
        service_request = service_request_service.get_or_404(request_id)

        # Check if user is the customer of this request
        if service_request.customer_id != current_user:
            return (
                jsonify({"error": "Only the customer can complete this request"}),
                403,
            )

        # Complete the service request
        completed_request = service_request_service.complete_service(
            request_id=request_id, completion_data=data
        )

        service_request_schema = ServiceRequestSchema()
        return (
            jsonify(
                {
                    "message": "Service completed successfully",
                    "service_request": service_request_schema.dump(completed_request),
                }
            ),
            200,
        )
    except ValidationException as e:
        return jsonify({"error": e.message}), e.code
    except ResourceNotFoundException as e:
        return jsonify({"error": e.message}), e.code
    except ServiceException as e:
        return jsonify({"error": e.message}), e.code


@service_request_bp.route("/<int:request_id>/start", methods=["POST"])
@jwt_required()
def start_service(request_id):
    """Start a service (professional only)"""
    current_user = get_jwt_identity()

    try:
        # Get the service request
        service_request = service_request_service.get_or_404(request_id)

        # Check if user is the assigned professional
        if service_request.professional_id != current_user["id"]:
            return (
                jsonify(
                    {"error": "Only the assigned professional can start this service"}
                ),
                403,
            )

        # Update service request status to in progress
        updated_request = service_request_service.update(
            id=request_id, status="in_progress"
        )

        service_request_schema = ServiceRequestSchema()
        return (
            jsonify(
                {
                    "message": "Service started successfully",
                    "service_request": service_request_schema.dump(updated_request),
                }
            ),
            200,
        )
    except ValidationException as e:
        return jsonify({"error": e.message}), e.code
    except ResourceNotFoundException as e:
        return jsonify({"error": e.message}), e.code
    except ServiceException as e:
        return jsonify({"error": e.message}), e.code


@service_request_bp.route("/<int:request_id>/accept", methods=["POST"])
@jwt_required()
def accept_request(request_id):
    """Accept a service request (professional only)"""
    current_user = get_jwt_identity()

    # Check if user is a professional
    if current_user.get("role") != "PROFESSIONAL":
        return jsonify({"error": "Only professionals can accept requests"}), 403

    try:
        # Get professional's ID
        from app.services import ProfessionalService
        professional_service = ProfessionalService()
        professional = professional_service.get_by_user_id(current_user["id"])
        
        if not professional:
            return jsonify({"error": "Professional profile not found"}), 404
            
        if not professional.is_verified:
            return jsonify({"error": "Your account must be verified to accept requests"}), 403

        # Accept the service request
        updated_request = service_request_service.accept_request(
            request_id=request_id, professional_id=professional.id
        )

        service_request_schema = ServiceRequestSchema()
        return (
            jsonify(
                {
                    "message": "Service request accepted successfully",
                    "service_request": service_request_schema.dump(updated_request),
                }
            ),
            200,
        )
    except ValidationException as e:
        return jsonify({"error": e.message}), e.code
    except ResourceNotFoundException as e:
        return jsonify({"error": e.message}), e.code
    except ServiceException as e:
        return jsonify({"error": e.message}), e.code


@service_request_bp.route("/<int:request_id>/cancel", methods=["POST"])
@jwt_required()
def cancel_service(request_id):
    """Cancel a service request (customer only)"""
    current_user = get_jwt_identity()

    try:
        # Get the service request
        service_request = service_request_service.get_or_404(request_id)

        # Check if user is the customer of this request
        if service_request.customer_id != current_user["id"]:
            return jsonify({"error": "Only the customer can cancel this request"}), 403

        # Update service request status to cancelled
        updated_request = service_request_service.update(
            id=request_id, status="cancelled"
        )

        service_request_schema = ServiceRequestSchema()
        return (
            jsonify(
                {
                    "message": "Service cancelled successfully",
                    "service_request": service_request_schema.dump(updated_request),
                }
            ),
            200,
        )
    except ValidationException as e:
        return jsonify({"error": e.message}), e.code
    except ResourceNotFoundException as e:
        return jsonify({"error": e.message}), e.code
    except ServiceException as e:
        return jsonify({"error": e.message}), e.code
