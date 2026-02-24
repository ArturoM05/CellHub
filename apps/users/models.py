"""
apps/users/models.py

Usuario personalizado de CellHub.
Principio SRP: Solo gestiona datos y comportamiento del usuario.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Usuario de CellHub extendido con datos adicionales.
    Hereda de AbstractUser para no reinventar autenticación.
    """
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.username} ({self.email})"

    def get_full_info(self) -> dict:
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'phone': self.phone,
            'first_name': self.first_name,
            'last_name': self.last_name,
        }
