import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

celery_app = Celery('cellhub')
# Leer configuración de Django (con prefijo CELERY_ si se usa)
celery_app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks en apps instaladas
celery_app.autodiscover_tasks()

@celery_app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
    return 'ok'
