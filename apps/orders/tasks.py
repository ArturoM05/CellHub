from __future__ import annotations

from celery import shared_task
from core.notifications.interfaces import OrderNotificationService


@shared_task(bind=True)
def notify_order_confirmed(self, user_email: str, user_phone: str, order_id: int):
    """Tarea asíncrona para notificar confirmación de orden."""
    try:
        notifier = OrderNotificationService()
        notifier.notify_order_confirmed(user_email=user_email, user_phone=user_phone, order_id=order_id)
        return {'status': 'ok', 'order_id': order_id}
    except Exception as e:
        # Re-raise para que Celery pueda reintentar según configuración
        raise
