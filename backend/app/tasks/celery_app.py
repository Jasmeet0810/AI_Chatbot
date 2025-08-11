from celery import Celery
from ..config import settings
import logging

logger = logging.getLogger(__name__)

# Create Celery app
celery_app = Celery(
    "lazulite_ppt_generator",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=['app.tasks.ppt_tasks']
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Task routes
celery_app.conf.task_routes = {
    'app.tasks.ppt_tasks.generate_ppt_task': {'queue': 'ppt_generation'},
    'app.tasks.ppt_tasks.cleanup_old_files_task': {'queue': 'maintenance'},
}

# Periodic tasks
celery_app.conf.beat_schedule = {
    'cleanup-old-files': {
        'task': 'app.tasks.ppt_tasks.cleanup_old_files_task',
        'schedule': 3600.0,  # Run every hour
    },
}

logger.info("Celery app configured successfully")