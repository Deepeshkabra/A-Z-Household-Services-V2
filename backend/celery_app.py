from flask import Flask
from app import create_app
from app.celery_config import configure_celery

app = create_app()
with app.app_context():
    celery = configure_celery(app)

# # Import tasks to ensure they are registered with Celery
import app.tasks