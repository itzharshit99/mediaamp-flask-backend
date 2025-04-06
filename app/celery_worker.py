from celery import Celery
from app import create_app

flask_app = create_app()

celery = Celery(
    flask_app.import_name,
    broker='redis://redis:6379/0',  # Direct Redis URL
    backend='redis://redis:6379/0',
    include=['app.tasks.daily_loader']
)

# Update Celery config from Flask app
celery.conf.update(
    result_expires=3600,
    task_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    enable_utc=True
)

# Import tasks after celery is created
from app.tasks import daily_loader