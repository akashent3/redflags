"""Celery application configuration for background tasks."""

from celery import Celery
from celery.schedules import crontab

from app.config import settings

# Create Celery app
celery_app = Celery(
    "redflags",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks.analysis_tasks", "app.tasks.watchlist_tasks", "app.tasks.export_tasks"],  # Auto-discover tasks
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,  # 10 minutes max per task
    task_soft_time_limit=540,  # 9 minutes soft limit (warning)
    worker_prefetch_multiplier=1,  # Process one task at a time
    task_acks_late=True,  # Acknowledge task after completion
    task_reject_on_worker_lost=True,
    result_expires=3600,  # Results expire after 1 hour
)

# Optional: Configure task routes for different queues
celery_app.conf.task_routes = {
    "app.tasks.analysis_tasks.analyze_report_task": {"queue": "analysis"},
}

# Configure beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    'check-watchlist-alerts-daily': {
        'task': 'app.tasks.watchlist_tasks.check_watchlist_alerts',
        'schedule': crontab(hour=8, minute=0),  # 8 AM UTC daily
    },
    'send-weekly-digest': {
        'task': 'app.tasks.watchlist_tasks.send_weekly_digest',
        'schedule': crontab(day_of_week=1, hour=9, minute=0),  # Monday 9 AM UTC
    },
}

if __name__ == "__main__":
    celery_app.start()
