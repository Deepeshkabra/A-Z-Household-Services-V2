import os
from datetime import timedelta

# Base directory of the application
basedir = os.path.abspath(os.path.dirname(__file__))


# Create the folder if it doesn't exist
# Note: Environment variables are loaded from .env file in app/__init__.py


class Config:
    """Base configuration."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "default-secret-key")
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable tracking modifications
    SQLALCHEMY_DATABASE_URI = (
        f"sqlite:///{os.path.join(basedir, 'project_database.db')}"  # SQLite file path
    )
    
    # Celery Configuration
    broker_url = os.environ.get('broker_url', 'redis://localhost:6379/0')
    result_backend = os.environ.get('result_backend', 'redis://localhost:6379/0')
    timezone = 'UTC'
    enable_utc = True

    # Admin credentials
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@example.com")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")
    ADMIN_NAME = os.environ.get("ADMIN_NAME", "Administrator")

    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)  # 1 hour
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)  # 30 days
    JWT_TOKEN_LOCATION = ['headers']

    # File Upload Configuration
    UPLOAD_FOLDER = os.path.join(basedir, "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size
    ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}

    # Ensure upload directory exists
    @staticmethod
    def init_app(app):
        """Initialize application instance with additional steps."""
        # Create upload folders
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'professional_documents'), exist_ok=True)

    # Pagination Configuration
    DEFAULT_PAGE_SIZE = 10
    MAX_PAGE_SIZE = 100

    # Service Request Configuration
    SERVICE_REQUEST_STATUSES = [
        "pending",
        "accepted",
        "in_progress",
        "completed",
        "cancelled",
    ]

    # Email Configuration (placeholder for future implementation)
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.example.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "true").lower() in ["true", "on", "1"]
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "user@example.com")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "password")
    MAIL_DEFAULT_SENDER = os.environ.get(
        "MAIL_DEFAULT_SENDER", "atozhouseholdservicesv2@gmail.com"
    )


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", Config.SQLALCHEMY_DATABASE_URI
    )


class TestingConfig(Config):
    """Testing configuration."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
