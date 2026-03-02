"""apps/cart/views.py"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from apps.products.models import Product
from apps.inventory.models import Inventory
from .models import Cart, CartItem
from .serializers import CartSerializer, AddToCartSerializer, CartItemSerializer


class CartView(APIView):
    """GET /api/v1/cart/ — Ver carrito del usuario."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return Response(CartSerializer(cart).data)


class CartItemView(APIView):
    """POST /api/v1/cart/items/ — Agregar o actualizar ítem en carrito."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product = get_object_or_404(Product, pk=serializer.validated_data['product_id'], is_active=True)
        quantity = serializer.validated_data['quantity']

        # Verificar stock
        try:
            inventory = product.inventory
            if not inventory.check_availability(quantity):
                return Response(
                    {'error': f'Stock insuficiente. Disponible: {inventory.stock_available}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Inventory.DoesNotExist:
            return Response({'error': 'Producto sin inventario registrado'}, status=400)

        cart, _ = Cart.objects.get_or_create(user=request.user)
        item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not created:
            item.quantity += quantity
        else:
            item.quantity = quantity
        item.save()

        return Response(
            CartItemSerializer(item).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )


class CartItemDeleteView(APIView):
    """DELETE /api/v1/cart/items/{id}/ — Eliminar ítem del carrito."""
    permission_classes = [IsAuthenticated]

    def delete(self, request, item_id):
        cart = get_object_or_404(Cart, user=request.user)
        item = get_object_or_404(CartItem, pk=item_id, cart=cart)
        item.delete()
        return Response({'message': 'Producto eliminado del carrito'}, status=status.HTTP_204_NO_CONTENT)
