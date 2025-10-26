from .routes import bp
from .auth import auth_bp
from .user import user_bp
from .admin import admin_bp
from .professional import professional_bp
from .service_request import service_request_bp

__all__ = [
    "bp",
    "auth_bp",
    "user_bp",
    "admin_bp",
    "professional_bp",
    "service_request_bp",
]
