"""
apps/orders/models.py
Modelos: Order, OrderItem, Purchase (Compra rápida con Factory)
"""
from django.db import models


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending',   'Pendiente'),
        ('confirmed', 'Confirmado'),
        ('shipped',   'Enviado'),
        ('delivered', 'Entregado'),
        ('cancelled', 'Cancelado'),
    ]
    VALID_TRANSITIONS = {
        'pending':   ['confirmed', 'cancelled'],
        'confirmed': ['shipped', 'cancelled'],
        'shipped':   ['delivered'],
        'delivered': [],
        'cancelled': [],
    }

    user             = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='orders')
    shipping_address = models.ForeignKey('shipping.Address', on_delete=models.PROTECT)
    payment_method   = models.CharField(max_length=50)
    total            = models.DecimalField(max_digits=12, decimal_places=2)
    status           = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes            = models.TextField(blank=True)
    transaction_id   = models.CharField(max_length=100, blank=True)
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Orden'
        verbose_name_plural = 'Ordenes'

    def __str__(self):
        return f"Orden #{self.id} — {self.user.username} — ${self.total:,.0f} — {self.get_status_display()}"

    def change_status(self, new_status):
        allowed = self.VALID_TRANSITIONS.get(self.status, [])
        if new_status not in allowed:
            raise ValueError(f"Transicion invalida: {self.status} → {new_status}. Permitidas: {allowed}")
        self.status = new_status
        self.save(update_fields=['status', 'updated_at'])


class OrderItem(models.Model):
    order      = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product    = models.ForeignKey('products.Product', on_delete=models.PROTECT)
    quantity   = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        verbose_name = 'Item de orden'
        verbose_name_plural = 'Items de orden'

    def __str__(self):
        return f"{self.quantity}x {self.product} @ ${self.unit_price:,.0f}"

    def get_subtotal(self):
        if self.unit_price is None or self.quantity is None:
            return 0
        return self.unit_price * self.quantity


class Purchase(models.Model):
    """
    Compra rapida de un producto.
    Al guardarse:
      1. Verifica stock en inventario
      2. Usa PaymentFactory para procesar el pago (Factory Pattern)
      3. Descuenta el inventario automaticamente
    """
    PAYMENT_CHOICES = [
        ('credit_card', 'Tarjeta de Credito'),
        ('debit_card',  'Tarjeta Debito'),
        ('pse',         'PSE'),
        ('nequi',       'Nequi'),
        ('davivienda',  'Davivienda'),
    ]
    STATUS_CHOICES = [
        ('approved', 'Aprobado'),
        ('pending',  'Pendiente'),
        ('rejected', 'Rechazado'),
    ]

    user           = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='purchases', verbose_name='Usuario')
    product        = models.ForeignKey('products.Product', on_delete=models.PROTECT, verbose_name='Producto')
    quantity       = models.PositiveIntegerField(default=1, verbose_name='Cantidad')
    unit_price     = models.DecimalField(max_digits=12, decimal_places=2, editable=False, default=0, verbose_name='Precio unitario')
    total          = models.DecimalField(max_digits=12, decimal_places=2, editable=False, default=0, verbose_name='Total')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='credit_card', verbose_name='Metodo de pago')
    status         = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', editable=False, verbose_name='Estado')
    transaction_id = models.CharField(max_length=100, blank=True, editable=False, verbose_name='ID Transaccion')
    purchased_at   = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de compra')

    class Meta:
        ordering = ['-purchased_at']
        verbose_name = 'Compra'
        verbose_name_plural = 'Compras'

    def __str__(self):
        return f"Compra #{self.id} — {self.user.username} — {self.product} x{self.quantity} — {self.get_status_display()}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if is_new:
            self.unit_price = self.product.price
            self.total = self.product.price * self.quantity

            inventory = self.product.inventory
            if not inventory.check_availability(self.quantity):
                raise ValueError(
                    f"Stock insuficiente para {self.product}. "
                    f"Disponible: {inventory.stock_available}, solicitado: {self.quantity}"
                )

            # Factory Pattern: obtiene y ejecuta el procesador correcto
            from core.factories.payment_factory import PaymentFactory
            processor = PaymentFactory.get_processor(self.payment_method)
            result = processor.process(float(self.total), {
                'card_number': '0000000000004242',
                'cvv': '123',
                'expiry': '12/26',
                'cardholder_name': self.user.get_full_name() or self.user.username,
                'bank_code': '001',
                'document_type': 'CC',
                'document_number': '123456',
                'phone_number': getattr(self.user, 'phone', '3000000000'),
                'account_number': '123456',
            })

            self.status = result['status']
            self.transaction_id = result.get('transaction_id', '')

            if self.status in ('approved', 'pending'):
                inventory.reserve_stock(self.quantity)

        super().save(*args, **kwargs)
