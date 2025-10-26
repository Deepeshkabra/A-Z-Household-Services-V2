from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services import AdminService, UserService, ValidationException, ServiceException, ResourceNotFoundException
from app.schemas.schema import UserSchema, ServiceSchema
from marshmallow import ValidationError
from app.models.models import Service
from sqlalchemy.exc import SQLAlchemyError
import traceback
import logging

logger = logging.getLogger(__name__)

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def get_all_users():
    """Get all users (admin only)"""
    current_user_id = get_jwt_identity()
    from flask_jwt_extended import get_jwt
    jwt_data = get_jwt()
    
    # Check if user is admin
    if jwt_data.get('role') != 'ADMIN':
        return jsonify({'error': 'Unauthorized access'}), 403
    
    try:
        user_service = UserService()
        users = user_service.get_all_users()
        user_schema = UserSchema(many=True)
        return jsonify(user_schema.dump(users)), 200
    except ServiceException as e:
        logger.error(f"Service exception getting all users: {e.message}")
        return jsonify({'error': e.message}), e.code
    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving users: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': 'Database error occurred while retrieving users'}), 500
    except Exception as e:
        logger.error(f"Unexpected error retrieving users: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': 'An unexpected error occurred'}), 500


@admin_bp.route('/users/<int:user_id>/block', methods=['POST'])
@jwt_required()
def block_user(user_id):
    """Block a user (admin only)"""
    current_user = get_jwt_identity()
    data = request.get_json()
    
    # Check if user is admin
    if current_user.get('role') != 'ADMIN':
        return jsonify({'error': 'Unauthorized access'}), 403
    
    if not data or 'reason' not in data:
        return jsonify({'error': 'Reason for blocking is required'}), 400
    
    try:
        AdminService.block_user(
            user_id=user_id,
            blocked_by=current_user['id'],
            reason=data['reason']
        )
        return jsonify({'message': 'User blocked successfully'}), 200
    except ValidationException as e:
        logger.error(f"Validation exception blocking user {user_id}: {e.message}")
        return jsonify({'error': e.message}), e.code
    except ResourceNotFoundException as e:
        logger.error(f"Resource not found blocking user {user_id}: {e.message}")
        return jsonify({'error': e.message}), e.code
    except ServiceException as e:
        logger.error(f"Service exception blocking user {user_id}: {e.message}")
        return jsonify({'error': e.message}), e.code
    except SQLAlchemyError as e:
        logger.error(f"Database error blocking user {user_id}: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': 'Database error occurred while blocking user'}), 500
    except Exception as e:
        logger.error(f"Unexpected error blocking user {user_id}: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': 'An unexpected error occurred'}), 500

@admin_bp.route('/services', methods=['GET', 'POST'])

def services():
    """Get all services or create a new service (admin only)"""
    # Import get_jwt inside the function to avoid circular imports
    
    
    # Get current user ID and JWT data

    
    if request.method == 'GET':
        # GET method - Retrieve all services
        try:
            # Query all active services
            services = Service.query.filter_by(is_active=True).all()
            
            # Serialize services data
            service_schema = ServiceSchema(many=True)
            serialized_services = service_schema.dump(services)
            
            return jsonify(serialized_services), 200
            
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving services: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({'error': 'Database error occurred while retrieving services'}), 500
        except Exception as e:
            logger.error(f"Unexpected error retrieving services: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({'error': 'An unexpected error occurred'}), 500
    
    elif request.method == 'POST':
        # POST method - Create a new service
        data = request.get_json()
        
        # Validate request data exists
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        try:
            # Validate service data using schema
            service_schema = ServiceSchema()
            service_data = service_schema.load(data)
            
            # Create service using admin service
            service = AdminService.create_service(service_data=service_data)
            
            # Return success response with created service data
            return jsonify({
                'message': 'Service created successfully',
                'service': service_schema.dump(service)
            }), 201
            
        except ValidationError as e:
            # Handle marshmallow validation errors
            error_messages = str(e)
            logger.error(f"Validation error creating service: {error_messages}")
            return jsonify({'error': error_messages}), 422
            
        except ValidationException as e:
            # Handle custom validation exceptions
            logger.error(f"Validation exception creating service: {e.message}")
            return jsonify({'error': e.message}), e.code
            
        except ServiceException as e:
            # Handle service-specific exceptions
            logger.error(f"Service exception creating service: {e.message}")
            return jsonify({'error': e.message}), e.code
            
        except SQLAlchemyError as e:
            # Handle database errors
            logger.error(f"Database error creating service: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({'error': 'Database error occurred while creating service'}), 500
            
        except Exception as e:
            # Handle unexpected errors
            logger.error(f"Unexpected error creating service: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({'error': 'An unexpected error occurred'}), 500

@admin_bp.route('/professionals/verify/<int:professional_id>', methods=['POST'])
@jwt_required()
def verify_professional(professional_id):
    """Verify a professional's documents (admin only)"""
    current_user_id = get_jwt_identity()
    from flask_jwt_extended import get_jwt
    jwt_data = get_jwt()
    
    # Check if user is admin
    if jwt_data.get('role') != 'ADMIN':
        return jsonify({'error': 'Unauthorized access'}), 403
    
    try:
        from app.services import ProfessionalService
        professional_service = ProfessionalService()
        
        professional_service.verify_documents(
            professional_id=professional_id,
            verified_by=current_user_id
        )
        
        return jsonify({'message': 'Professional documents verified successfully'}), 200
    except ValidationException as e:
        logger.error(f"Validation exception verifying professional {professional_id}: {e.message}")
        return jsonify({'error': e.message}), e.code
    except ResourceNotFoundException as e:
        logger.error(f"Resource not found verifying professional {professional_id}: {e.message}")
        return jsonify({'error': e.message}), e.code
    except ServiceException as e:
        logger.error(f"Service exception verifying professional {professional_id}: {e.message}")
        return jsonify({'error': e.message}), e.code
    except SQLAlchemyError as e:
        logger.error(f"Database error verifying professional {professional_id}: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': 'Database error occurred while verifying professional'}), 500
    except Exception as e:
        logger.error(f"Unexpected error verifying professional {professional_id}: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': 'An unexpected error occurred'}), 500

@admin_bp.route('/professionals/reject/<int:professional_id>', methods=['POST'])
@jwt_required()
def reject_professional(professional_id):
    """Reject a professional's verification (admin only)"""
    current_user_id = get_jwt_identity()
    from flask_jwt_extended import get_jwt
    jwt_data = get_jwt()
    
    # Check if user is admin
    if jwt_data.get('role') != 'ADMIN':
        return jsonify({'error': 'Unauthorized access'}), 403
    
    try:
        from app.services import ProfessionalService
        from app.models.models import Professional
        from app.extensions import db
        
        # Get the professional
        professional = Professional.query.get_or_404(professional_id)
        
        # Update status
        professional.is_verified = False
        
        db.session.commit()
        
        return jsonify({'message': 'Professional verification rejected successfully'}), 200
    except Exception as e:
        logger.error(f"Error rejecting professional {professional_id}: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': 'An error occurred while rejecting professional'}), 500

@admin_bp.route('/professionals/reset/<int:professional_id>', methods=['POST'])
@jwt_required()
def reset_professional_status(professional_id):
    """Reset a professional's verification status (admin only)"""
    current_user_id = get_jwt_identity()
    from flask_jwt_extended import get_jwt
    jwt_data = get_jwt()
    
    # Check if user is admin
    if jwt_data.get('role') != 'ADMIN':
        return jsonify({'error': 'Unauthorized access'}), 403
    
    try:
        from app.services import ProfessionalService
        from app.models.models import Professional
        from app.extensions import db
        
        # Get the professional
        professional = Professional.query.get_or_404(professional_id)
        
        # Reset status
        professional.is_verified = False
        
        db.session.commit()
        
        return jsonify({'message': 'Professional verification status reset successfully'}), 200
    except Exception as e:
        logger.error(f"Error resetting professional status {professional_id}: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': 'An error occurred while resetting professional status'}), 500

@admin_bp.route('/professionals', methods=['GET'])
@jwt_required()
def get_all_professionals():
    """Get all professionals with their details (admin only)"""
    from flask_jwt_extended import get_jwt
    jwt_data = get_jwt()
    
    # Check if user is admin
    if jwt_data.get('role') != 'ADMIN':
        return jsonify({'error': 'Unauthorized access'}), 403
    
    try:
        from app.models.models import Professional
        from app.schemas.schema import ProfessionalSchema
        
        # Query all active professionals
        professionals = Professional.query.filter_by(is_active=True).all()
        
        # Serialize professionals data with nested relationships
        professional_schema = ProfessionalSchema(many=True)
        serialized_professionals = professional_schema.dump(professionals)
        
        return jsonify(serialized_professionals), 200
    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving professionals: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': 'Database error occurred while retrieving professionals'}), 500
    except Exception as e:
        logger.error(f"Unexpected error retrieving professionals: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': 'An unexpected error occurred'}), 500


@admin_bp.route('/customers', methods=['GET'])
@jwt_required()
def get_all_customers():
    """Get all customers with their details (admin only)"""
    from flask_jwt_extended import get_jwt
    jwt_data = get_jwt()
    
    # Check if user is admin
    if jwt_data.get('role') != 'ADMIN':
        return jsonify({'error': 'Unauthorized access'}), 403
    
    try:
        from app.models.models import Customer
        from app.schemas.schema import CustomerSchema

        # Query all active customers
        customers = Customer.query.filter_by(is_active=True).all()

        # Serialize customers data with nested relationships
        customer_schema = CustomerSchema(many=True)
        serialized_customers = customer_schema.dump(customers)
        return jsonify(serialized_customers), 200
    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving professionals: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': 'Database error occurred while retrieving professionals'}), 500
    except Exception as e:
        logger.error(f"Unexpected error retrieving professionals: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': 'An unexpected error occurred'}), 500

@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def get_dashboard_stats():
    """Get admin dashboard statistics"""
    current_user_id = get_jwt_identity()
    from flask_jwt_extended import get_jwt
    jwt_data = get_jwt()
    
    # Check if user is admin
    if jwt_data.get('role') != 'ADMIN':
        return jsonify({'error': 'Unauthorized access'}), 403
    
    try:
        # This would typically fetch various statistics from the database
        # For now, we'll just return a placeholder response
        return jsonify({
            'total_users': 0,
            'total_professionals': 0,
            'total_service_requests': 0,
            'pending_verifications': 0,
            'recent_activities': []
        }), 200
    except SQLAlchemyError as e:
        logger.error(f"Database error retrieving dashboard stats: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': 'Database error occurred while retrieving dashboard statistics'}), 500
    except Exception as e:
        logger.error(f"Unexpected error retrieving dashboard stats: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': 'An unexpected error occurred'}), 500

@admin_bp.route('/export/service-requests', methods=['POST'])
@jwt_required()
def export_service_requests():
    """Trigger an asynchronous job to export service requests as CSV"""
    current_user_id = get_jwt_identity()
    from flask_jwt_extended import get_jwt
    jwt_data = get_jwt()
    
    # Check if user is admin
    if jwt_data.get('role') != 'ADMIN':
        return jsonify({'error': 'Unauthorized access'}), 403
    
    # Get filter parameters from request
    filters = request.get_json() or {}
    
    try:
        # Import the task
        from app.tasks import generate_csv_export
        from celery import current_app as celery_app
        
        # Start the task asynchronously
        task = celery_app.send_task('app.tasks.generate_csv_export', 
                                   args=[current_user_id], 
                                   kwargs={'filters': filters})
        
        # Return the task ID for status checking
        return jsonify({
            'message': 'CSV export job started successfully',
            'job_id': task.id,
            'status': 'processing'
        }), 202
    except Exception as e:
        logger.error(f"Error starting CSV export job: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': 'Error starting CSV export job'}), 500

@admin_bp.route('/export/status/<job_id>', methods=['GET'])
@jwt_required()
def check_export_status(job_id):
    """Check the status of an export job"""
    current_user_id = get_jwt_identity()
    from flask_jwt_extended import get_jwt
    jwt_data = get_jwt()
    
    # Check if user is admin
    if jwt_data.get('role') != 'ADMIN':
        return jsonify({'error': 'Unauthorized access'}), 403
    
    try:
        # Import AsyncResult to check task status
        from celery.result import AsyncResult
        
        # Get task result
        task_result = AsyncResult(job_id)
        
        # Check task status
        if task_result.state == 'PENDING':
            response = {
                'job_id': job_id,
                'status': 'pending',
                'message': 'Export job is pending'
            }
        elif task_result.state == 'FAILURE':
            response = {
                'job_id': job_id,
                'status': 'failed',
                'message': 'Export job failed'
            }
        elif task_result.ready():
            result = task_result.get()
            if result:
                # Get filename from the result path
                filename = os.path.basename(result)
                response = {
                    'job_id': job_id,
                    'status': 'completed',
                    'message': 'Export job completed successfully',
                    'file_url': f'/api/admin/export/download/{filename}'
                }
            else:
                response = {
                    'job_id': job_id,
                    'status': 'failed',
                    'message': 'Export job completed but no file was generated'
                }
        else:
            response = {
                'job_id': job_id,
                'status': 'processing',
                'message': 'Export job is still processing'
            }
        
        return jsonify(response), 200
    except Exception as e:
        logger.error(f"Error checking export status: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': 'Error checking export status'}), 500

@admin_bp.route('/export/download/<filename>', methods=['GET'])
@jwt_required()
def download_export(filename):
    """Download a generated CSV export file"""
    current_user_id = get_jwt_identity()
    from flask_jwt_extended import get_jwt
    jwt_data = get_jwt()
    
    # Check if user is admin
    if jwt_data.get('role') != 'ADMIN':
        return jsonify({'error': 'Unauthorized access'}), 403
    
    try:
        # Construct the file path
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'exports', filename)
        
        # Check if file exists
        if not os.path.exists(file_path):
            return jsonify({'error': 'Export file not found'}), 404
        
        # Return the file as an attachment
        return send_file(file_path, as_attachment=True, download_name=filename)
    except Exception as e:
        logger.error(f"Error downloading export file: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({'error': 'Error downloading export file'}), 500