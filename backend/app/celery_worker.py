from celery import Celery

celery_app = Celery(
    "worker",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
)

celery_app.conf.task_routes = {
    "app.services.jobs.*": {"queue": "jobs"},
    "app.services.resumes.*": {"queue": "resumes"},
}
