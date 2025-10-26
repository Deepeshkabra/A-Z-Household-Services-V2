from app.models.models import User, Service
from flask import current_app
from app.extensions import db
from .base_service import (
    ServiceException,
    ValidationException,
    ResourceNotFoundException,
)
from sqlalchemy.exc import IntegrityError, SQLAlchemyError


class AdminService:
    @staticmethod
    def block_user(user_id: int, blocked_by: int, reason: str) -> bool:
        """Block a user (customer or professional)"""
        if user_id is None or blocked_by is None:
            raise ValidationException("User ID and blocked_by ID cannot be None")
        if not reason:
            raise ValidationException("Reason for blocking must be provided")

        user = User.query.get(user_id)
        if not user:
            raise ResourceNotFoundException(f"User with ID {user_id} not found")

        try:
            user.is_active = False
            user.updated_by = blocked_by
            db.session.commit()
            return True
        except IntegrityError as e:
            db.session.rollback()
            raise ValidationException(f"Validation error blocking user: {str(e)}")
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ServiceException(f"Error blocking user: {str(e)}")

    @staticmethod
    def create_service(service_data: dict) -> Service:
        """Create a new service type"""
        if not service_data:
            raise ValidationException("Service data cannot be empty")


        # Check if service with this name already exists
        if (
            "name" in service_data
            and Service.query.filter_by(name=service_data["name"]).first()
        ):
            raise ValidationException("Service with this name already exists")

        try:
            service = Service(**service_data)
            db.session.add(service)
            db.session.commit()
            return service
        except IntegrityError as e:
            db.session.rollback()
            raise ValidationException(f"Validation error creating service: {str(e)}")
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ServiceException(f"Error creating service: {str(e)}")
