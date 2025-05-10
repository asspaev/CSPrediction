from celery import Celery

from core import settings

celery_app = Celery(
    "celery_app",
    broker=settings.celery.broker,
    backend=settings.celery.backend,
    include=[  # <-- явно указываем, откуда таски
        "tasks.predict",  # модуль tasks/predict.py
    ],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)

# celery_app.autodiscover_tasks(["tasks"])
