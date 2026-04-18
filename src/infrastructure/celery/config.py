import os
from celery import Celery
from celery.schedules import crontab

# URL de Redis (desde env vars o default local)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

app = Celery('newsbrief_worker')

# Configuración básica
app.conf.update(
    broker_url=REDIS_URL,
    result_backend=REDIS_URL,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    # Importante para async/await en tareas
    worker_prefetch_multiplier=1, 
)

app.conf.beat_schedule = {
    'generate-all-daily-briefings': {
        'task': 'tasks.trigger_all_users_briefings', # Ver siguiente punto
        'schedule': crontab(hour=8, minute=0), # Cada día a las 8:00 UTC
    },
}
from src.infrastructure.celery import tasks