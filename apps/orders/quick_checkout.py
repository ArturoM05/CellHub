"""
apps/orders/quick_checkout.py

Endpoint de checkout rápido para el frontend.
Crea dirección temporal + orden en un solo paso.
No requiere dirección previa guardada.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from apps.cart.models import Cart
from apps.shipping.models import Address
from apps.products.models import Product
from core.builders.order_builder import OrderBuilder


class QuickCheckoutView(APIView):
    """
    POST /api/v1/orders/quick-checkout/

    Crea una orden directamente desde el carrito del usuario.
    Usa una dirección de envío provisional si no tiene ninguna.

    Body (JSON):
    {
        "full_name": "Juan Pérez",
        "city": "Bogotá",
        "street": "Cra 7 # 32-16",
        "phone": "3001234567",
        "payment_method": "credit_card"   (opcional, default: credit_card)
    }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        data = request.data

        # Validar campos mínimos
        required = ['full_name', 'city', 'street', 'phone']
        missing = [f for f in required if not data.get(f)]
        if missing:
            return Response(
                {'error': 'Campos requeridos: ' + ', '.join(missing)},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Obtener o crear carrito
        try:
            cart = Cart.objects.prefetch_related('items__product').get(user=user)
        except Cart.DoesNotExist:
            return Response({'error': 'No tienes un carrito activo'}, status=400)

        if not cart.items.exists():
            return Response({'error': 'Tu carrito está vacío'}, status=400)

        # Crear dirección provisional
        address = Address.objects.create(
            user=user,
            full_name=data['full_name'],
            city=data['city'],
            department=data.get('department', data['city']),
            neighborhood=data.get('neighborhood', 'Centro'),
            street=data['street'],
            reference=data.get('reference', ''),
            phone=data['phone'],
            is_default=False,
        )

        # Construir orden con el Builder Pattern
        builder = OrderBuilder(user=user)
        for item in cart.items.all():
            builder.add_item(
                product=item.product,
                quantity=item.quantity,
                price=float(item.product.price),
            )

        payment_method = data.get('payment_method', 'credit_card')

        try:
            order = (builder
                .set_shipping_address(address)
                .set_payment_method(payment_method)
                .add_notes('Pedido desde tienda web')
                .build()
            )
        except ValueError as e:
            address.delete()  # limpiar dirección si falla
            return Response({'error': str(e)}, status=400)

        # Vaciar carrito
        cart.clear()

        return Response({
            'success': True,
            'order_id': order.id,
            'total': float(order.total),
            'status': order.status,
            'message': f'¡Orden #{order.id} creada exitosamente! Revisa el admin para ver el detalle.',
        }, status=status.HTTP_201_CREATED)


class GuestLoginView(APIView):
    """
    POST /api/v1/users/guest-login/
    Login rápido para el frontend — devuelve JWT.
    """
    permission_classes = []

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if not user:
            return Response({'error': 'Credenciales incorrectas'}, status=401)

        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
            }
        })


class AddToCartAPIView(APIView):
    """
    POST /api/v1/cart/add/
    Agrega un producto al carrito del usuario autenticado.
    Body: { "product_id": 1, "quantity": 1 }
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_id = request.data.get('product_id')
        quantity   = int(request.data.get('quantity', 1))

        try:
            product = Product.objects.get(pk=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response({'error': 'Producto no encontrado'}, status=404)

        # Verificar stock
        try:
            if not product.inventory.check_availability(quantity):
                return Response(
                    {'error': f'Stock insuficiente. Disponible: {product.inventory.stock_available}'},
                    status=400
                )
        except Exception:
            return Response({'error': 'Producto sin inventario'}, status=400)

        cart, _ = Cart.objects.get_or_create(user=request.user)

        from apps.cart.models import CartItem
        item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            item.quantity += quantity
        else:
            item.quantity = quantity
        item.save()

        # Devolver carrito actualizado
        items = []
        for i in cart.items.select_related('product').all():
            items.append({
                'id': i.id,
                'product_id': i.product.id,
                'name': f'{i.product.brand} {i.product.model_name}',
                'price': float(i.product.price),
                'quantity': i.quantity,
                'subtotal': float(i.product.price * i.quantity),
            })

        return Response({
            'message': 'Producto agregado al carrito',
            'cart': {
                'items': items,
                'total': float(cart.get_total()),
                'count': cart.items.count(),
            }
        })


class GetCartAPIView(APIView):
    """GET /api/v1/cart/summary/ — Resumen del carrito para el frontend."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        items = []
        for i in cart.items.select_related('product').all():
            items.append({
                'id': i.id,
                'product_id': i.product.id,
                'name': f'{i.product.brand} {i.product.model_name}',
                'price': float(i.product.price),
                'quantity': i.quantity,
                'subtotal': float(i.product.price * i.quantity),
            })
        return Response({
            'items': items,
            'total': float(cart.get_total()),
            'count': cart.items.count(),
        })


class RemoveCartItemAPIView(APIView):
    """DELETE /api/v1/cart/remove/{item_id}/"""
    permission_classes = [IsAuthenticated]

    def delete(self, request, item_id):
        from apps.cart.models import CartItem
        try:
            item = CartItem.objects.get(pk=item_id, cart__user=request.user)
            item.delete()
        except CartItem.DoesNotExist:
            return Response({'error': 'Item no encontrado'}, status=404)

        cart = Cart.objects.get(user=request.user)
        return Response({
            'message': 'Eliminado',
            'total': float(cart.get_total()),
            'count': cart.items.count(),
        })
