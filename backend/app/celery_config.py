from celery import Celery
from celery.schedules import crontab
import os

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['result_backend'],
        broker=app.config['broker_url']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

def configure_celery(app):
    app.config.update(
        broker_url=os.environ.get('broker_url', 'redis://localhost:6379/0'),
        result_backend=os.environ.get('result_backend', 'redis://localhost:6379/0'),
        timezone='UTC',
        enable_utc=True,
        beat_schedule={
            'send-daily-reminders': {
                'task': 'app.tasks.send_daily_reminders',
                'schedule': crontab(hour=18, minute=0),  # Run at 6:00 PM every day
            },
            'generate-monthly-reports': {
                'task': 'app.tasks.generate_monthly_reports',
                'schedule': crontab(day_of_month=1, hour=0, minute=0),  # Run on the 1st of every month
            },
        }
    )
    return make_celery(app)