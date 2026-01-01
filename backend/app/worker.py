"""
Celery worker configuration and tasks for the Home Aid Kit Manager.
"""

from celery import Celery
from app.core.config import settings

# Create Celery instance
celery = Celery(
    "home_aid_kit_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.external_links",
        "app.tasks.medication_sync",
    ]
)

# Configure Celery
celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_serializer_kwargs={'ensure_ascii': False},
    result_expires=3600,  # 1 hour
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_disable_rate_limits=False,
    task_default_retry_delay=60,  # 1 minute
    task_max_retries=3,
)

# Autodiscover tasks
celery.autodiscover_tasks()

if __name__ == '__main__':
    celery.start()
