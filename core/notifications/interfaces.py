"""
core/notifications/interfaces.py

Principio ISP: Interfaces pequeñas y específicas.
Cada clase implementa solo las que necesita.
"""
from abc import ABC, abstractmethod


class EmailNotifier(ABC):
    @abstractmethod
    def send_email(self, to: str, subject: str, body: str) -> None:
        pass


class SMSNotifier(ABC):
    @abstractmethod
    def send_sms(self, phone: str, message: str) -> None:
        pass


class PushNotifier(ABC):
    @abstractmethod
    def send_push(self, user_id: int, message: str) -> None:
        pass


# ── Implementaciones concretas ──────────────────────────────────────────────

class ConsoleEmailService(EmailNotifier):
    """Implementación de email para desarrollo (imprime en consola)."""

    def send_email(self, to: str, subject: str, body: str) -> None:
        print(f"\n📧 EMAIL → {to}")
        print(f"   Asunto: {subject}")
        print(f"   {body}\n")


class ConsoleSMSService(SMSNotifier):
    """Implementación SMS para desarrollo."""

    def send_sms(self, phone: str, message: str) -> None:
        print(f"\n📱 SMS → {phone}: {message}\n")


class OrderNotificationService(ConsoleEmailService, ConsoleSMSService):
    """
    Servicio que implementa Email + SMS para notificaciones de órdenes.
    Principio ISP: Solo implementa lo que necesita.
    """

    def notify_order_confirmed(self, user_email: str, user_phone: str, order_id: int):
        self.send_email(
            to=user_email,
            subject=f'✅ Orden #{order_id} confirmada - CellHub',
            body=f'Tu pedido #{order_id} fue confirmado y está siendo procesado.'
        )
        self.send_sms(
            phone=user_phone,
            message=f'CellHub: Tu orden #{order_id} fue confirmada. ¡Gracias!'
        )

    def notify_order_shipped(self, user_email: str, order_id: int, tracking: str):
        self.send_email(
            to=user_email,
            subject=f'🚚 Orden #{order_id} en camino - CellHub',
            body=f'Tu pedido está en camino. Tracking: {tracking}'
        )
