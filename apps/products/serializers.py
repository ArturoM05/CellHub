"""
apps/products/serializers.py
Principio SRP: Solo serializa/deserializa datos de productos.
"""
from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    os_display = serializers.CharField(source='get_os_display', read_only=True)
    stock = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'brand', 'model_name', 'price', 'description', 'image',
            'ram_gb', 'storage_gb', 'processor', 'battery_mah',
            'camera_mp', 'screen_inches', 'os', 'os_display',
            'is_active', 'created_at', 'stock',
        ]

    def get_stock(self, obj) -> int:
        inventory = getattr(obj, 'inventory', None)
        return inventory.stock_available if inventory else 0


class ProductSpecsSerializer(serializers.Serializer):
    """Serializer para el endpoint /specs/"""
    specifications = serializers.DictField()
    product_name   = serializers.CharField()
    price          = serializers.DecimalField(max_digits=12, decimal_places=2)
