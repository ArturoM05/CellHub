"""
apps/orders/services.py

Principio SRP: Lógica de negocio de órdenes separada de las vistas.
Principio DIP: Depende de abstracciones (PaymentProcessor, EmailNotifier).
Usa OrderBuilder para construir órdenes.
"""
from core.builders.order_builder import OrderBuilder
from core.factories.payment_factory import PaymentFactory
from core.notifications.interfaces import OrderNotificationService


class OrderService:
    """
    Servicio principal de órdenes.

    Principio DIP: recibe dependencias por constructor,
    no las instancia directamente.
    """

    def __init__(self):
        # En producción, estas dependencias vendrían de un contenedor DI
        self.notifier = OrderNotificationService()

    def create_order_from_cart(self, user, address_id: int, payment_method: str, notes: str = '') -> dict:
        """
        Crea una orden a partir del carrito del usuario.
        Usa el OrderBuilder (Builder Pattern).
        """
        from apps.cart.models import Cart
        from apps.shipping.models import Address

        # Obtener carrito y dirección
        cart = Cart.objects.prefetch_related('items__product').get(user=user)

        if not cart.items.exists():
            raise ValueError("El carrito está vacío")

        address = Address.objects.get(pk=address_id, user=user)

        # Construir la orden con el Builder
        builder = OrderBuilder(user=user)

        for item in cart.items.all():
            builder.add_item(
                product=item.product,
                quantity=item.quantity,
                price=float(item.product.price),
            )

        order = (builder
            .set_shipping_address(address)
            .set_payment_method(payment_method)
            .add_notes(notes)
            .build()
        )

        # Vaciar el carrito
        cart.clear()

        return order

    def confirm_payment(self, order_id: int, payment_data: dict) -> dict:
        """
        Procesa el pago de una orden usando el PaymentFactory.
        Principio Factory: el procesador se obtiene según el método.
        """
        from apps.orders.models import Order

        order = Order.objects.select_related('user').get(pk=order_id)

        # Factory Pattern: obtiene el procesador correcto
        processor = PaymentFactory.get_processor(order.payment_method)

        if not processor.validate(payment_data):
            raise ValueError("Datos de pago inválidos")

        result = processor.process(float(order.total), payment_data)

        if result['status'] == 'approved':
            order.transaction_id = result['transaction_id']
            order.save(update_fields=['transaction_id'])
            order.change_status('confirmed')

            # Notificar al usuario
            self.notifier.notify_order_confirmed(
                user_email=order.user.email,
                user_phone=getattr(order.user, 'phone', ''),
                order_id=order.id,
            )

        return {'order_id': order.id, 'payment_result': result}
