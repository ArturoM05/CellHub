from django.contrib import admin
from .models import Producto, Orden, OrdenItem

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre", "precio")


@admin.register(Orden)
class OrdenAdmin(admin.ModelAdmin):
    list_display = ("id", "usuario", "total", "estado")


@admin.register(OrdenItem)
class OrdenItemAdmin(admin.ModelAdmin):
    list_display = ("orden", "producto", "cantidad")
