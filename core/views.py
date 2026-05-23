"""
Core views for system monitoring and health checks.
"""
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import redis
import logging

logger = logging.getLogger(__name__)


@api_view(['GET'])
def system_info(request):
    """
    GET /api/v1/system/info/
    Returns system health status, versions and broker connectivity.
    """
    info = {
        'service': 'cellhub',
        'version': '1.0.0',
        'environment': settings.DEBUG and 'development' or 'production',
        'database': {
            'status': 'connected',
            'backend': settings.DATABASES['default']['ENGINE'],
        },
        'broker': {
            'status': 'unavailable',
            'backend': getattr(settings, 'CELERY_BROKER_URL', 'not configured'),
        },
        'cache': {
            'status': 'unavailable',
            'backend': getattr(settings, 'CACHES', {}).get('default', {}).get('BACKEND', 'not configured'),
        },
    }

    # Check Redis broker
    try:
        broker_url = getattr(settings, 'CELERY_BROKER_URL', '')
        if broker_url and 'redis' in broker_url:
            r = redis.from_url(broker_url)
            r.ping()
            info['broker']['status'] = 'connected'
    except Exception as e:
        logger.warning(f"Redis broker check failed: {e}")
        info['broker']['status'] = 'error'

    # Check Celery workers (optional: count active tasks/workers)
    try:
        from celery.app.control import Inspect
        from config.celery import celery_app
        insp = Inspect(app=celery_app)
        active = insp.active()
        info['celery'] = {
            'status': 'connected' if active is not None else 'unreachable',
            'workers': len(active) if active else 0,
        }
    except Exception as e:
        logger.warning(f"Celery inspection failed: {e}")
        info['celery'] = {'status': 'error'}

    return Response(info, status=status.HTTP_200_OK)
