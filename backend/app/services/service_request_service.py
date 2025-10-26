from datetime import datetime
from typing import List
from app.models.models import ServiceRequest, ServiceStatus, Review, Professional
from app.extensions import db
from .base_service import BaseService, ServiceException, ValidationException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError


class ServiceRequestService(BaseService):
    def __init__(self):
        super().__init__(ServiceRequest)

    def create_request(self, customer_id: int, **data) -> ServiceRequest:
        """Create a new service request"""
        try:
            request = ServiceRequest(
                customer_id=customer_id, status=ServiceStatus.REQUESTED, **data
            )
            db.session.add(request)
            db.session.commit()
            return request
        except IntegrityError as e:
            db.session.rollback()
            raise ValidationException(
                f"Validation error creating service request: {str(e)}"
            )
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ServiceException(f"Error creating service request: {str(e)}")

    def assign_professional(
        self, request_id: int, professional_id: int
    ) -> ServiceRequest:
        """Assign a professional to a service request"""
        if request_id is None or professional_id is None:
            raise ValidationException("Request ID and professional ID cannot be None")

        request = self.get_or_404(request_id)
        if request.status != ServiceStatus.REQUESTED:
            raise ValidationException("Request cannot be assigned in current status")

        try:
            request.professional_id = professional_id
            request.status = ServiceStatus.ASSIGNED
            db.session.commit()
            return request
        except IntegrityError as e:
            db.session.rollback()
            raise ValidationException(
                f"Validation error assigning professional: {str(e)}"
            )
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ServiceException(f"Error assigning professional: {str(e)}")

    def get_by_customer_id(self, customer_id: int) -> List[ServiceRequest]:
        """Get all service requests for a specific customer"""
        if customer_id is None:
            raise ValidationException("Customer ID cannot be None")

        try:
            return ServiceRequest.query\
                .filter_by(customer_id=customer_id)\
                .all()
        except SQLAlchemyError as e:
            raise ServiceException(
                f"Error retrieving requests for customer {customer_id}: {str(e)}"
            )

    def get_by_professional_id(self, professional_id: int) -> List[ServiceRequest]:
        """Get all service requests for a specific professional"""
        if professional_id is None:
            raise ValidationException("Professional ID cannot be None")

        try:
            return ServiceRequest.query\
                .filter_by(professional_id=professional_id)\
                .all()
        except SQLAlchemyError as e:
            raise ServiceException(
                f"Error retrieving requests for professional {professional_id}: {str(e)}"
            )
    
    def get_available_requests_by_service(self, service_id: int) -> List[ServiceRequest]:
        """Get all available service requests for a specific service type"""
        if service_id is None:
            raise ValidationException("Service ID cannot be None")

        try:
            return ServiceRequest.query\
                .filter_by(service_id=service_id, status=ServiceStatus.REQUESTED)\
                .filter(ServiceRequest.professional_id.is_(None))\
                .all()
        except SQLAlchemyError as e:
            raise ServiceException(
                f"Error retrieving available requests for service {service_id}: {str(e)}"
            )
    
    def accept_request(self, request_id: int, professional_id: int) -> ServiceRequest:
        """Professional accepts a service request"""
        if request_id is None or professional_id is None:
            raise ValidationException("Request ID and professional ID cannot be None")

        request = self.get_or_404(request_id)
        
        # Check if request is available
        if request.status != ServiceStatus.REQUESTED or request.professional_id is not None:
            raise ValidationException("Request is not available for acceptance")
            
        # Check if professional exists and is verified
        professional = Professional.query.filter_by(id=professional_id, is_verified=True).first()
        if not professional:
            raise ValidationException("Professional not found or not verified")
            
        # Check if professional provides the requested service
        if professional.service_id != request.service_id:
            raise ValidationException("Professional does not provide the requested service")

        try:
            request.professional_id = professional_id
            request.status = ServiceStatus.ASSIGNED
            db.session.commit()
            return request
        except IntegrityError as e:
            db.session.rollback()
            raise ValidationException(
                f"Validation error accepting request: {str(e)}"
            )
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ServiceException(f"Error accepting request: {str(e)}")
    
    def complete_service(
        self, request_id: int, completion_data: dict
    ) -> ServiceRequest:
        """Complete a service request and create review"""
        if request_id is None or not completion_data:
            raise ValidationException("Request ID and completion data are required")

        request = self.get_or_404(request_id)
        if request.status != ServiceStatus.IN_PROGRESS:
            raise ValidationException("Request is not in progress")

        try:
            db.session.begin_nested()

            # Update request status
            request.status = ServiceStatus.COMPLETED
            request.completion_date = datetime.utcnow()
            request.customer_remarks = completion_data.get("remarks")

            # Create review if provided
            if "rating" in completion_data:
                if not request.professional_id:
                    raise ValidationException(
                        "Cannot add review: No professional assigned"
                    )

                review = Review(
                    service_request_id=request_id,
                    customer_id=request.customer_id,
                    professional_id=request.professional_id,
                    rating=completion_data["rating"],
                    comment=completion_data.get("review_comment"),
                )
                db.session.add(review)

                # Update professional's rating
                professional = request.professional
                if professional:
                    total_reviews = professional.total_reviews + 1
                    new_rating = (
                        (professional.rating * professional.total_reviews)
                        + completion_data["rating"]
                    ) / total_reviews
                    professional.rating = new_rating
                    professional.total_reviews = total_reviews

            db.session.commit()
            return request
        except IntegrityError as e:
            db.session.rollback()
            raise ValidationException(f"Validation error completing service: {str(e)}")
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ServiceException(f"Error completing service: {str(e)}")
