from django.contrib import admin
from .models import Producto

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("marca", "modelo", "precio", "activo")
    search_fields = ("marca", "modelo")