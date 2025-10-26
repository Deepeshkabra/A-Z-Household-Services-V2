from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.ext.declarative import declared_attr
from enum import Enum
from app.extensions import db



class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    is_active = db.Column(db.Boolean, default=True)

   

    def save(self):
        db.session.add(self)
        try:
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e


class UserRole(Enum):
    ADMIN = "ADMIN"
    PROFESSIONAL = "PROFESSIONAL"
    CUSTOMER = "CUSTOMER"

    def __str__(self):
        return self.value
        
        
        



class User(BaseModel):
    __tablename__ = "users"

    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False)
    phone = db.Column(db.String(20), unique=True, index=True)
    name = db.Column(db.String(100), nullable=False)

    last_login = db.Column(db.DateTime)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Customer(BaseModel):
    __tablename__ = "customers"

    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False
    )
    location = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(10), index=True)
    rating = db.Column(db.Float, default=0.0)

    user = db.relationship(
        "User", foreign_keys=[user_id], backref=db.backref("customer", uselist=False)
    )


class Professional(BaseModel):
    __tablename__ = "professionals"

    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False
    )
    service_id = db.Column(db.Integer, db.ForeignKey("services.id"), nullable=False)
    experience_years = db.Column(db.Float, nullable=False)
    bio = db.Column(db.Text)
    document_verified = db.Column(db.Boolean, default=False)
    rating = db.Column(db.Float, default=0.0)
    total_reviews = db.Column(db.Integer, default=0)
    location = db.Column(db.String(100), nullable=False)
    pincode = db.Column(db.String(10), index=True)
    is_verified = db.Column(db.Boolean, default=False)

    user = db.relationship(
        "User",
        foreign_keys=[user_id],
        backref=db.backref("professional", uselist=False),
    )
    service = db.relationship("Service", backref=db.backref("professionals"))


class Service(BaseModel):
    __tablename__ = "services"

    name = db.Column(db.String(100), nullable=False, unique=True)
    # db.Numeric(10, 2): This specifies the data type of the column. Numeric(10, 2) means that the column will store numeric values with up to 10 digits in total, and 2 of those digits can be after the decimal point. This is typically used for monetary values.
    base_price = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.Text)
    estimated_time = db.Column(db.Integer)  # in minutes
    category = db.Column(db.String(50), index=True)
    is_available = db.Column(db.Boolean, default=True)


class ServiceStatus(Enum):
    REQUESTED = "requested"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

    def __str__(self):
        return self.value


class ServiceRequest(BaseModel):  # Changed from db.Model to BaseModel
    __tablename__ = "service_requests"

    # Remove redundant columns that are already in BaseModel
    service_id = db.Column(db.Integer, db.ForeignKey("services.id"), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey("professionals.id"))
    request_time = db.Column(db.DateTime)
    status = db.Column(db.Enum(ServiceStatus))
    location = db.Column(db.String(200), nullable=False)
    pin_code = db.Column(db.String(20), nullable=False)

    service = db.relationship("Service", backref="requests")
    customer = db.relationship(
        "Customer", foreign_keys=[customer_id], backref="service_requests"
    )
    professional = db.relationship(
        "Professional", foreign_keys=[professional_id], backref="service_requests"
    )


class Review(BaseModel):
    __tablename__ = "reviews"

    id = db.Column(db.Integer, primary_key=True)
    service_request_id = db.Column(
        db.Integer, db.ForeignKey("service_requests.id"), nullable=False
    )
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    Customer_remarks = db.Column(db.Text)
    Professional_remarks = db.Column(db.Text)

    service_request = db.relationship("ServiceRequest", backref="reviews")


class ProfessionalDocument(BaseModel):
    __tablename__ = "professional_documents"

    professional_id = db.Column(
        db.Integer, db.ForeignKey("professionals.id"), nullable=False
    )
    document_type = db.Column(db.String(50), nullable=False)
    document_url = db.Column(db.String(255), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    verified_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    verification_date = db.Column(db.DateTime, nullable=True)

    professional = db.relationship(
        "Professional", backref=db.backref("documents", lazy=True)
    )
    verifier = db.relationship(
        "User", foreign_keys=[verified_by], backref="verified_documents"
    )
