from flask import Flask
from config import Config, TestingConfig, DevelopmentConfig, ProductionConfig
from .extensions import db, migrate, jwt, cors
from .routes.routes import bp
from .routes.auth import auth_bp
from .routes.user import user_bp
from .routes.admin import admin_bp
from .routes.professional import professional_bp
from .routes.service_request import service_request_bp
from dotenv import load_dotenv
import os
import logging

# Load environment variables from .env file
load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def create_app(config_class=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize app with config-specific settings
    if hasattr(config_class, 'init_app'):
        config_class.init_app(app)

    # JWT configuration is now handled in config.py

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    # Initialize CORS with default settings to allow requests from any origin
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    with app.app_context():
        db.create_all()

    # Register all blueprints
    app.register_blueprint(bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(professional_bp)
    app.register_blueprint(service_request_bp)

    return app


__all__ = ["create_app"]
