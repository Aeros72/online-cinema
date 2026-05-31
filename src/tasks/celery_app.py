from celery import Celery

from src.core.config import settings

celery_app = Celery(
    "online_cinema",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["src.tasks.cleanup_tokens"],
)

celery_app.conf.beat_schedule = {
    "cleanup-expired-tokens-every-hour": {
        "task": "cleanup_expired_tokens",
        "schedule": 3600.0,
    },
}

celery_app.conf.timezone = "UTC"
