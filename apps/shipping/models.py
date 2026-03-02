"""apps/shipping/models.py"""
from django.db import models


class Address(models.Model):
    user        = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='addresses')
    full_name   = models.CharField(max_length=150, verbose_name='Nombre completo')
    city        = models.CharField(max_length=100, verbose_name='Ciudad')
    department  = models.CharField(max_length=100, verbose_name='Departamento')
    neighborhood= models.CharField(max_length=100, verbose_name='Barrio')
    street      = models.CharField(max_length=200, verbose_name='Dirección')
    reference   = models.CharField(max_length=200, blank=True, verbose_name='Referencia')
    phone       = models.CharField(max_length=20, verbose_name='Teléfono de contacto')
    is_default  = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Dirección'
        verbose_name_plural = 'Direcciones'

    def __str__(self):
        return f"{self.street}, {self.neighborhood}, {self.city}"

    def save(self, *args, **kwargs):
        # Si se marca como predeterminada, quitar la anterior
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)
