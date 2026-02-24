"""
apps/products/models.py

Principio SRP: Solo representa el dominio de Producto.
"""
from django.db import models


class Product(models.Model):
    OS_CHOICES = [
        ('android', 'Android'),
        ('ios', 'iOS'),
        ('other', 'Otro'),
    ]

    brand        = models.CharField(max_length=100, verbose_name='Marca')
    model_name   = models.CharField(max_length=100, verbose_name='Modelo')
    price        = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Precio')
    description  = models.TextField(verbose_name='Descripción')
    image        = models.ImageField(upload_to='products/', null=True, blank=True)
    is_active    = models.BooleanField(default=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    # Especificaciones técnicas
    ram_gb        = models.PositiveIntegerField(verbose_name='RAM (GB)')
    storage_gb    = models.PositiveIntegerField(verbose_name='Almacenamiento (GB)')
    processor     = models.CharField(max_length=150, verbose_name='Procesador')
    battery_mah   = models.PositiveIntegerField(verbose_name='Batería (mAh)')
    camera_mp     = models.PositiveIntegerField(verbose_name='Cámara (MP)')
    screen_inches = models.DecimalField(max_digits=4, decimal_places=2, verbose_name='Pantalla (pulgadas)')
    os            = models.CharField(max_length=20, choices=OS_CHOICES, verbose_name='Sistema Operativo')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'

    def __str__(self):
        return f"{self.brand} {self.model_name}"

    def get_specifications(self) -> dict:
        """SRP: el producto sabe cómo exponer sus especificaciones."""
        return {
            'RAM': f'{self.ram_gb} GB',
            'Almacenamiento': f'{self.storage_gb} GB',
            'Procesador': self.processor,
            'Batería': f'{self.battery_mah} mAh',
            'Cámara principal': f'{self.camera_mp} MP',
            'Pantalla': f'{self.screen_inches}"',
            'Sistema operativo': self.get_os_display(),
        }

    def update_price(self, new_price: float) -> None:
        """Actualiza el precio con validación."""
        if new_price <= 0:
            raise ValueError("El precio debe ser positivo")
        self.price = new_price
        self.save(update_fields=['price'])
