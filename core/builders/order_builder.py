"""
core/builders/order_builder.py

Patrón Builder: Construye órdenes complejas paso a paso.
Fluent interface permite encadenar métodos.
"""


class OrderBuilder:
    """
    Builder para construir órdenes de forma legible y validada.

    Uso:
        order = (OrderBuilder(user=request.user)
            .add_item(product1, quantity=2, price=1500000)
            .add_item(product2, quantity=1, price=800000)
            .set_shipping_address(address)
            .set_payment_method('pse')
            .add_notes('Entregar en portería')
            .build()
        )
    """

    def __init__(self, user):
        self._user = user
        self._items: list[dict] = []
        self._shipping_address = None
        self._payment_method: str | None = None
        self._notes: str = ''

    def add_item(self, product, quantity: int, price: float) -> 'OrderBuilder':
        """Agrega un producto a la orden."""
        if quantity <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")
        if price <= 0:
            raise ValueError("El precio debe ser mayor a 0")
        self._items.append({
            'product': product,
            'quantity': quantity,
            'unit_price': price,
        })
        return self  # Fluent interface

    def set_shipping_address(self, address) -> 'OrderBuilder':
        """Define la dirección de envío."""
        self._shipping_address = address
        return self

    def set_payment_method(self, method: str) -> 'OrderBuilder':
        """Define el método de pago."""
        valid_methods = ['credit_card', 'debit_card', 'pse', 'nequi', 'davivienda']
        if method not in valid_methods:
            raise ValueError(f"Método '{method}' inválido. Opciones: {valid_methods}")
        self._payment_method = method
        return self

    def add_notes(self, notes: str) -> 'OrderBuilder':
        """Agrega notas opcionales a la orden."""
        self._notes = notes
        return self

    def _validate(self) -> None:
        """Valida que la orden tenga todo lo necesario antes de construirla."""
        if not self._items:
            raise ValueError("La orden debe tener al menos un producto")
        if not self._shipping_address:
            raise ValueError("La orden requiere una dirección de envío")
        if not self._payment_method:
            raise ValueError("La orden requiere un método de pago")

    def build(self):
        """
        Construye y persiste la orden en la base de datos.
        Retorna la instancia de Order creada.
        """
        # Import aquí para evitar importaciones circulares
        from apps.orders.models import Order, OrderItem

        self._validate()

        total = sum(
            item['quantity'] * item['unit_price']
            for item in self._items
        )

        order = Order.objects.create(
            user=self._user,
            shipping_address=self._shipping_address,
            payment_method=self._payment_method,
            total=total,
            notes=self._notes,
            status='pending',
        )

        for item_data in self._items:
            OrderItem.objects.create(order=order, **item_data)

        return order
