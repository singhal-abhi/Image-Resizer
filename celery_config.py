from celery import Celery

celery_worker = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=["main"],
)

celery_worker.conf.update(
    result_expires=3600,
)
