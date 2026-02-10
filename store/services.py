from typing import List, Dict
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
from .models import Producto, Inventario, Orden


class OrderBuilder:
    """Builds an Orden instance from input data and validates related inventory."""

    def __init__(self, user, items: List[Dict]):
        self.user = user
        self.items = items

    def validate(self):
        if not self.items:
            raise ValueError("No items provided for the order")
        for it in self.items:
            if "producto_id" not in it or "cantidad" not in it:
                raise ValueError("Each item must include 'producto_id' and 'cantidad'")
            if it["cantidad"] <= 0:
                raise ValueError("Cantidad must be positive")

    def build(self) -> Orden:
        self.validate()
        order = Orden(usuario=self.user)
        # total will be calculated by the service before saving
        return order


class NotificationSender:
    """Abstract notifier - real implementations could send email/SMS, etc."""

    def send(self, order: Orden):
        raise NotImplementedError()


class ConsoleNotificationSender(NotificationSender):
    def send(self, order: Orden):
        # Lightweight default for local development
        print(f"Order {order.pk} created for {order.usuario} - total={order.total}")


class NotificationFactory:
    @staticmethod
    def get_sender(kind: str = "console") -> NotificationSender:
        if kind == "console":
            return ConsoleNotificationSender()
        if kind == "email":
            return EmailNotificationSender()
        # Placeholder: extend for 'sms', etc. Default to console
        return ConsoleNotificationSender()


class EmailNotificationSender(NotificationSender):
    def send(self, order: Orden):
        subject = f"Order #{order.pk} created"
        message = f"Order {order.pk} for {order.usuario} total: {order.total}"
        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", None)
        recipient_list = [getattr(order.usuario, "email", None)]
        # If recipient email missing, fallback to console
        if not recipient_list[0]:
            return ConsoleNotificationSender().send(order)
        try:
            send_mail(subject, message, from_email, recipient_list)
        except Exception:
            # In production, log exception. Here, fallback silently.
            ConsoleNotificationSender().send(order)


class OrderService:
    """Orchestrates order creation, inventory updates and notifications."""

    def __init__(self, notifier_kind: str = "console"):
        self.notifier = NotificationFactory.get_sender(notifier_kind)

    @transaction.atomic
    def create_order(self, user, items: List[Dict]) -> Orden:
        """
        items: list of dicts with keys: producto_id, cantidad
        """
        builder = OrderBuilder(user, items)
        order = builder.build()

        # compute total and validate inventory
        total = 0
        for it in items:
            producto = Producto.objects.select_for_update().get(pk=it["producto_id"])
            cantidad = int(it["cantidad"])
            # check inventory
            inv = Inventario.objects.select_for_update().get(producto=producto)
            if not producto.activo:
                raise ValueError(f"Producto {producto} is not active")
            if cantidad > inv.stock:
                raise ValueError(f"Insufficient stock for {producto}")
            total += producto.precio * cantidad

        order.total = total
        order.save()

        # reduce stock
        for it in items:
            producto = Producto.objects.select_for_update().get(pk=it["producto_id"])
            inv = Inventario.objects.select_for_update().get(producto=producto)
            inv.descontar_stock(int(it["cantidad"]))

        # notify
        try:
            self.notifier.send(order)
        except Exception:
            # don't break the transaction for notifier failures; log in real app
            pass

        return order
from .builders import OrdenBuilder
from .factories import PagoFactory
from .models import Producto

class CheckoutService:

    def procesar_compra(self, usuario, productos_data, metodo_pago):
        builder = OrdenBuilder().para_usuario(usuario)

        for item in productos_data:
            producto = Producto.objects.get(
                id=item["producto_id"]
            )
            builder.agregar_producto(
                producto,
                item["cantidad"]
            )

        orden = builder.build()

        procesador_pago = PagoFactory.crear(metodo_pago)
        procesador_pago.pagar(orden.total)

        orden.estado = "PAGADA"
        orden.save()

        return orden
