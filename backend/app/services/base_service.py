from typing import Type, Optional, Any
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.models.models import BaseModel
from app.extensions import db


# Exceptions
class ServiceException(Exception):
    def __init__(self, message, code=400):
        self.message = message
        self.code = code
        super().__init__(self.message)


class ResourceNotFoundException(ServiceException):
    def __init__(self, message="Resource not found"):
        super().__init__(message, 404)


class ValidationException(ServiceException):
    def __init__(self, message="Validation failed"):
        super().__init__(message, 400)


# Base Service class
class BaseService:
    def __init__(self, model: Type[BaseModel]):
        self.model = model

    def get_by_id(self, id: int) -> Optional[BaseModel]:
        if id is None:
            return None
        return self.model.query.get(id)

    def get_or_404(self, id: int) -> BaseModel:
        if id is None:
            raise ValidationException("ID cannot be None")
        instance = self.get_by_id(id)
        if not instance:
            raise ResourceNotFoundException(
                f"{self.model.__name__} with ID {id} not found"
            )
        return instance

    def create(self, **data) -> BaseModel:
        try:
            instance = self.model(**data)
            db.session.add(instance)
            db.session.commit()
            return instance
        except IntegrityError as e:
            db.session.rollback()
            raise ValidationException(
                f"Validation error creating {self.model.__name__}: {str(e)}"
            )
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ServiceException(f"Error creating {self.model.__name__}: {str(e)}")

    def update(self, id: int, **data) -> BaseModel:
        instance = self.get_or_404(id)
        try:
            for key, value in data.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            db.session.commit()
            return instance
        except IntegrityError as e:
            db.session.rollback()
            raise ValidationException(
                f"Validation error updating {self.model.__name__}: {str(e)}"
            )
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ServiceException(f"Error updating {self.model.__name__}: {str(e)}")

    def delete(self, id: int) -> bool:
        instance = self.get_or_404(id)
        try:
            db.session.delete(instance)
            db.session.commit()
            return True
        except IntegrityError as e:
            db.session.rollback()
            raise ValidationException(
                f"Cannot delete {self.model.__name__} due to existing references: {str(e)}"
            )
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ServiceException(f"Error deleting {self.model.__name__}: {str(e)}")
