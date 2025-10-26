from datetime import datetime
from typing import List
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.models.models import Professional, User, UserRole, ProfessionalDocument
from app.extensions import db
from .base_service import BaseService, ServiceException, ValidationException


class ProfessionalService(BaseService):
    def __init__(self):
        super().__init__(Professional)

    def create_professional(
        self, user_data: dict, professional_data: dict
    ) -> Professional:
        """Create a new professional with associated user account"""
        if not user_data or not professional_data:
            raise ValidationException("User data and professional data cannot be empty")
        if "password_hash" not in user_data:
            raise ValidationException("Password is required for user creation")

        # Check if user with this email already exists
        if (
            "email" in user_data
            and User.query.filter_by(email=user_data["email"]).first()
        ):
            raise ValidationException("User with this email already exists")

        # Check if user with this phone already exists
        if (
            "phone" in user_data
            and User.query.filter_by(phone=user_data["phone"]).first()
        ):
            raise ValidationException("User with this phone number already exists")

        try:
            # Start transaction
            db.session.begin_nested()

            # Create user first
            user = User(**user_data)
            user.set_password(user_data["password_hash"])
            db.session.add(user)
            db.session.flush()  # Get user ID

            # Create professional profile
            professional = Professional(user_id=user.id, is_verified = False, **professional_data)
            db.session.add(professional)

            db.session.commit()
            return professional
        except IntegrityError as e:
            db.session.rollback()
            raise ValidationException(
                f"Validation error creating professional: {str(e)}"
            )
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ServiceException(f"Error creating professional: {str(e)}")

    def verify_documents(self, professional_id: int, verified_by: int) -> bool:
        """Verify professional's documents and update status"""
        if professional_id is None or verified_by is None:
            raise ValidationException("Professional ID and verifier ID cannot be None")

        professional = self.get_or_404(professional_id)
        try:
            unverified_docs = ProfessionalDocument.query.filter_by(
                professional_id=professional_id, is_verified=False
            ).all()

            if not unverified_docs:
                raise ValidationException("No unverified documents found")

            for doc in unverified_docs:
                doc.is_verified = True
                doc.verified_by = verified_by
                doc.verification_date = datetime.utcnow()

            professional.document_verified = True
            professional.is_verified = True
            db.session.commit()
            return True
        except IntegrityError as e:
            db.session.rollback()
            raise ValidationException(f"Validation error verifying documents: {str(e)}")
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ServiceException(f"Error verifying documents: {str(e)}")

    def get_available_professionals(
        self, service_id: int, pincode: str
    ) -> List[Professional]:
        """Get available professionals for a service in a location"""
        if service_id is None or not pincode:
            raise ValidationException("Service ID and pincode are required")

        return (
            Professional.query.filter_by(
                service_id=service_id, is_active=True, document_verified=True
            )
            .filter_by(pincode=pincode)
            .all()
        )
        
    def get_by_user_id(self, user_id: int) -> Professional:
        """Get professional by user ID"""
        if user_id is None:
            raise ValidationException("User ID cannot be None")
            
        professional = Professional.query.filter_by(user_id=user_id).first()
        if not professional:
            raise ValidationException(f"No professional found with user ID: {user_id}")
            
        return professional
