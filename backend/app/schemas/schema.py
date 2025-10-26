# schemas/base.py
from marshmallow import Schema, fields, validates, ValidationError, EXCLUDE
from datetime import datetime
from app.models import UserRole


class BaseSchema(Schema):
    class Meta:
        unknown = EXCLUDE  # Ignore unknown fields

    id = fields.Integer(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    is_active = fields.Boolean(dump_only=True)


# schemas/user.py
class UserSchema(BaseSchema):   
    email = fields.Email(required=True)
    password_hash = fields.String(required=True, load_only=True)
    name = fields.String(required=True)
    phone = fields.String(required=True)
    role = fields.Enum(UserRole, required=True)

    last_login = fields.DateTime(dump_only=True)

    @validates("password_hash")
    def validate_password(self, value):
        if len(value) < 8:
            raise ValidationError("Password must be at least 8 characters")
        if not any(char.isdigit() for char in value):
            raise ValidationError("Password must contain at least one number")
        if not any(char.isupper() for char in value):
            raise ValidationError("Password must contain at least one uppercase letter")

    @validates("phone")
    def validate_phone(self, value):
        import re

        if not re.match(r"^\+?1?\d{9,15}$", value):
            raise ValidationError("Invalid phone number format")


# schemas/customer.py


class CustomerSchema(BaseSchema):
    user_id = fields.Integer(dump_only=True)
    location = fields.String(required=True)
    rating = fields.Float(dump_only=True)
    pincode = fields.String(required=True)

    @validates("pincode")
    def validate_pincode(self, value):
        if not value.isdigit() or len(value) != 5:
            raise ValidationError("Invalid pincode format")


# schemas/professional.py
class ProfessionalSchema(BaseSchema):
    user_id = fields.Integer(dump_only=True)
    service_id = fields.Integer(required=True)
    experience_years = fields.Float(required=True)
    bio = fields.String()
    document_verified = fields.Boolean(dump_only=True, required=False)
    rating = fields.Float(dump_only=True)
    total_reviews = fields.Integer(dump_only=True)
    location = fields.String(required=True)
    pincode = fields.String(required=True)
    is_verified = fields.Boolean(dump_only=True)

    # Nested relationships
    user = fields.Nested("UserSchema", exclude=("password_hash",))
    service = fields.Nested("ServiceSchema")

    @validates("experience_years")
    def validate_experience(self, value):
        if value < 0:
            raise ValidationError("Experience years cannot be negative")
        if value > 50:
            raise ValidationError("Invalid experience years")

    @validates("pincode")
    def validate_pincode(self, value):
        if not value.isdigit() or len(value) != 5:
            raise ValidationError("Invalid pincode format")


# schemas/service.py
class ServiceSchema(BaseSchema):
    name = fields.String(required=True)
    base_price = fields.Decimal(required=True, places=2)
    description = fields.String()
    estimated_time = fields.Integer(required=True)
    category = fields.String(required=True)
    is_available = fields.Boolean()

    @validates("base_price")
    def validate_price(self, value):
        if value <= 0:
            raise ValidationError("Price must be greater than 0")

    @validates("estimated_time")
    def validate_time(self, value):
        if value <= 0:
            raise ValidationError("Estimated time must be greater than 0")


# schemas/service_request.py
class ServiceRequestSchema(BaseSchema):
    service_id = fields.Integer(required=True)
    customer_id = fields.Integer(dump_only=True)
    professional_id = fields.Integer()
    completion_date = fields.DateTime(dump_only=True)
    status = fields.String(dump_only=True)
    customer_remarks = fields.String()
    professional_remarks = fields.String()
    location = fields.String(required=True)
    pin_code = fields.String(required=True)
    price = fields.Decimal(places=2, dump_only=True)

    # Nested relationships
    service = fields.Nested("ServiceSchema")
    customer = fields.Nested("UserSchema", only=("id", "name", "email"))
    professional = fields.Nested("ProfessionalSchema", exclude=("user_id",))




# schemas/review.py
class ReviewSchema(BaseSchema):
    service_request_id = fields.Integer(required=True)
    rating = fields.Integer(required=True)
    comment = fields.String()

    # Nested relationships
    service_request = fields.Nested(
        "ServiceRequestSchema", exclude=("customer", "professional")
    )
    customer = fields.Nested("UserSchema", only=("id", "name"))
    professional = fields.Nested("ProfessionalSchema", only=("id", "user.name"))

    @validates("rating")
    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise ValidationError("Rating must be between 1 and 5")


# validators/custom_validators.py
from marshmallow import ValidationError
from datetime import datetime, timedelta


def validate_future_date(value):
    """Validate that a date is in the future"""
    if value <= datetime.now():
        raise ValidationError("Date must be in the future")


def validate_business_hours(value):
    """Validate that a datetime falls within business hours (9 AM - 6 PM)"""
    if not (9 <= value.hour < 18):
        raise ValidationError("Time must be between 9 AM and 6 PM")


def validate_working_days(value):
    """Validate that a date is not on weekend"""
    if value.weekday() in (5, 6):  # Saturday = 5, Sunday = 6
        raise ValidationError("Service cannot be scheduled on weekends")


# integration with services
class ServiceRequestValidator:
    @staticmethod
    def validate_create_request(data):
        schema = ServiceRequestSchema()
        validated_data = schema.load(data)

        # Additional business logic validation
        validate_future_date(validated_data["scheduled_date"])
        validate_business_hours(validated_data["scheduled_date"])
        validate_working_days(validated_data["scheduled_date"])

        return validated_data

    @staticmethod
    def validate_update_request(data):
        schema = ServiceRequestSchema(partial=True)
        return schema.load(data)
