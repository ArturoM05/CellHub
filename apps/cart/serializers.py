"""apps/cart/serializers.py"""
from rest_framework import serializers
from .models import Cart, CartItem
from apps.products.serializers import ProductSerializer


class CartItemSerializer(serializers.ModelSerializer):
    product_detail = ProductSerializer(source='product', read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_detail', 'quantity', 'subtotal', 'added_at']

    def get_subtotal(self, obj):
        return float(obj.get_subtotal())


class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity   = serializers.IntegerField(min_value=1, default=1)


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total', 'item_count', 'updated_at']

    def get_total(self, obj):
        return float(obj.get_total())

    def get_item_count(self, obj):
        return obj.items.count()
