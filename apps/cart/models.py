"""
apps/cart/models.py
Principio SRP: Solo maneja la lógica del carrito.
"""
from django.db import models


class Cart(models.Model):
    user       = models.OneToOneField('users.User', on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Carrito'

    def __str__(self):
        return f"Carrito de {self.user.username}"

    def get_total(self) -> float:
        """Calcula el total del carrito."""
        return sum(item.get_subtotal() for item in self.items.all())

    def clear(self) -> None:
        """Vacía el carrito después de una compra."""
        self.items.all().delete()


class CartItem(models.Model):
    cart      = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product   = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    quantity  = models.PositiveIntegerField(default=1)
    added_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['cart', 'product']
        verbose_name = 'Ítem de carrito'

    def __str__(self):
        return f"{self.quantity}x {self.product}"

    def get_subtotal(self) -> float:
        return self.product.price * self.quantity
