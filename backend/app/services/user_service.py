from datetime import datetime
from typing import Optional
from app.models.models import User, Customer
from app.extensions import db
from .base_service import BaseService, ServiceException, ValidationException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError


class UserService(BaseService):
    def __init__(self):
        super().__init__(User)

    def create_user(self, user_data: dict) -> User:
        """Create a new user"""
        if not user_data:
            raise ValidationException("User data cannot be empty")

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
            user = User(**user_data)
            if "password_hash" in user_data:
                user.set_password(user_data["password_hash"])
            db.session.add(user)
            db.session.commit()
            return user
        except IntegrityError as e:
            db.session.rollback()
            raise ValidationException(f"Validation error creating user: {str(e)}")
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ServiceException(f"Error creating user: {str(e)}")

    def authenticate(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user by email and password"""
        if not email or not password:
            return None

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            try:
                user.last_login = datetime.now()
                db.session.commit()
                return user
            except SQLAlchemyError:
                db.session.rollback()
                # Still return the user even if updating last_login fails
                return user
        return None

    def change_password(
        self, user_id: int, old_password: str, new_password: str
    ) -> bool:
        """Change user password"""
        if not old_password or not new_password:
            raise ValidationException("Password cannot be empty")

        user = self.get_or_404(user_id)
        if not user.check_password(old_password):
            raise ValidationException("Invalid old password")

        try:
            user.set_password(new_password)
            db.session.commit()
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ServiceException(f"Error changing password: {str(e)}")

    def update_profile(self, user_id: int, profile_data: dict) -> User:
        """Update user profile"""
        return self.update(user_id, **profile_data)

    def get_all_users(self):
        """Get all users"""
        return User.query.all()
        
    def create_customer(self, customer_data: dict) -> Customer:
        """Create a new customer profile"""
        if not customer_data:
            raise ValidationException("Customer data cannot be empty")
            
        if "user_id" not in customer_data:
            raise ValidationException("User ID is required for customer creation")
            
        try:
            # Create customer profile
            customer = Customer(**customer_data)
            db.session.add(customer)
            db.session.commit()
            return customer
        except IntegrityError as e:
            db.session.rollback()
            raise ValidationException(f"Validation error creating customer: {str(e)}")
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ServiceException(f"Error creating customer: {str(e)}")
