from __future__ import annotations

from celery import shared_task
from core.notifications.interfaces import OrderNotificationService
from django.utils.translation import gettext as _
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def notify_order_confirmed(self, user_email: str, user_phone: str, order_id: int):
    """Tarea asíncrona para notificar confirmación de orden."""
    try:
        notifier = OrderNotificationService()
        notifier.notify_order_confirmed(user_email=user_email, user_phone=user_phone, order_id=order_id)
        logger.info(f"Order confirmation notification sent for order {order_id}")
        return {'status': 'ok', 'order_id': order_id}
    except Exception as e:
        logger.error(f"Failed to notify order {order_id}: {e}")
        # Retry con backoff exponencial
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=2)
def audit_order_event(self, order_id: int, event_type: str, details: str = ''):
    """
    Log order events for audit trail (created, confirmed, shipped, cancelled).
    """
    try:
        # En producción, guardar a modelo AuditLog o servicio externo
        logger.info(f"AUDIT: Order {order_id} event='{event_type}' details='{details}'")
        return {'status': 'logged', 'order_id': order_id, 'event': event_type}
    except Exception as exc:
        logger.error(f"Audit log failed for order {order_id}: {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True)
def generate_sales_report(self, start_date: str, end_date: str):
    """
    Generate periodic sales report (daily/weekly/monthly).
    Puede ser schedulered via celery-beat.
    """
    from apps.orders.models import Order
    from datetime import datetime
    try:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        
        orders = Order.objects.filter(created_at__range=[start, end])
        total_revenue = sum(float(o.total_amount or 0) for o in orders)
        order_count = orders.count()
        
        report = {
            'period': f"{start_date} to {end_date}",
            'order_count': order_count,
            'total_revenue': total_revenue,
        }
        logger.info(f"Sales report generated: {report}")
        return report
    except Exception as exc:
        logger.error(f"Sales report generation failed: {exc}")
        return {'status': 'error', 'message': str(exc)}
