"""
apps/inventory/models.py
Principio SRP: Solo maneja el stock de productos.
"""
from django.db import models


class Inventory(models.Model):
    product         = models.OneToOneField('products.Product', on_delete=models.CASCADE, related_name='inventory')
    stock_available = models.PositiveIntegerField(default=0, verbose_name='Stock disponible')
    stock_reserved  = models.PositiveIntegerField(default=0, verbose_name='Stock reservado')
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Inventario'
        verbose_name_plural = 'Inventarios'

    def __str__(self):
        return f"Inventario: {self.product} ({self.stock_available} disponibles)"

    def check_availability(self, quantity: int) -> bool:
        """Verifica si hay stock suficiente."""
        return self.stock_available >= quantity

    def reserve_stock(self, quantity: int) -> None:
        """Reserva stock al confirmar una orden."""
        if not self.check_availability(quantity):
            raise ValueError(f"Stock insuficiente. Disponible: {self.stock_available}")
        self.stock_available -= quantity
        self.stock_reserved += quantity
        self.save(update_fields=['stock_available', 'stock_reserved'])

    def release_stock(self, quantity: int) -> None:
        """Libera stock reservado (ej: orden cancelada)."""
        self.stock_reserved -= quantity
        self.stock_available += quantity
        self.save(update_fields=['stock_available', 'stock_reserved'])

    def add_stock(self, quantity: int) -> None:
        """Agrega stock (nueva mercancía)."""
        self.stock_available += quantity
        self.save(update_fields=['stock_available'])
