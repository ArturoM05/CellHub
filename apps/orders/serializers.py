"""apps/orders/serializers.py"""
from rest_framework import serializers
from .models import Order, OrderItem
from apps.shipping.serializers import AddressSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    product_name  = serializers.CharField(source='product.model_name', read_only=True)
    product_brand = serializers.CharField(source='product.brand', read_only=True)
    subtotal      = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_brand', 'product_name', 'quantity', 'unit_price', 'subtotal']

    def get_subtotal(self, obj):
        return float(obj.get_subtotal())


class OrderSerializer(serializers.ModelSerializer):
    items            = OrderItemSerializer(many=True, read_only=True)
    shipping_address = AddressSerializer(read_only=True)
    status_display   = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'items', 'shipping_address', 'payment_method',
                  'total', 'status', 'status_display', 'notes',
                  'transaction_id', 'created_at']


class CreateOrderSerializer(serializers.Serializer):
    """Serializer para crear una nueva orden desde el carrito."""
    address_id     = serializers.IntegerField()
    payment_method = serializers.ChoiceField(choices=[
        'credit_card', 'debit_card', 'pse', 'nequi', 'davivienda'
    ])
    notes = serializers.CharField(required=False, allow_blank=True, default='')


class ChangeStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)
