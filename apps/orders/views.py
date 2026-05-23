"""apps/orders/views.py"""
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Order
from .serializers import OrderSerializer, CreateOrderSerializer, ChangeStatusSerializer
from .services import OrderService


class OrderListCreateView(generics.ListAPIView):
    """GET /api/v1/orders/ — Historial de órdenes del usuario."""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items__product')


class CreateOrderView(APIView):
    """POST /api/v1/orders/ — Crea orden desde el carrito. Usa OrderBuilder."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = OrderService()
        try:
            order = service.create_order_from_cart(
                user=request.user,
                address_id=serializer.validated_data['address_id'],
                payment_method=serializer.validated_data['payment_method'],
                notes=serializer.validated_data.get('notes', ''),
            )
        except (ValueError, Exception) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderDetailView(generics.RetrieveAPIView):
    """GET /api/v1/orders/{id}/ — Detalle de una orden."""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class ChangeOrderStatusView(APIView):
    """PATCH /api/v1/orders/{id}/status/ — Cambia estado de la orden."""
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        order = get_object_or_404(Order, pk=pk, user=request.user)
        serializer = ChangeStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            order.change_status(serializer.validated_data['status'])
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(OrderSerializer(order).data)


class SubmitOrderToAllyView(APIView):
    """
    POST /api/v1/orders/submit-to-ally/
    Envía orden a servicio aliado para fulfillment (usando Adapter pattern).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from core.adapters.third_party import RequestsThirdPartyAdapter, MockThirdPartyAdapter
        from django.conf import settings
        
        order_id = request.data.get('order_id')
        if not order_id:
            return Response({'error': 'order_id required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.get(pk=order_id, user=request.user)
            
            # Preparar datos para envío
            order_data = {
                'items': [
                    {'external_id': item.product.id, 'quantity': item.quantity}
                    for item in order.items.all()
                ],
                'shipping_address': {
                    'street': getattr(order, 'shipping_address', ''),
                    'city': 'Bogotá',
                },
                'customer_email': request.user.email,
            }
            
            # Usar adapter
            use_mock = getattr(settings, 'USE_MOCK_ADAPTER', True)
            adapter = MockThirdPartyAdapter() if use_mock else RequestsThirdPartyAdapter(
                base_url=getattr(settings, 'ALLY_SERVICE_URL', 'https://api.ally.local'),
                api_key=getattr(settings, 'ALLY_API_KEY', None)
            )
            
            result = adapter.submit_order(order_data)
            
            # Enqueue audit task
            from apps.orders.tasks import audit_order_event
            audit_order_event.delay(order.id, 'submitted_to_ally', f"External order: {result.get('external_order_id')}")
            
            return Response({
                'status': 'success',
                'external_order_id': result.get('external_order_id'),
                'eta': result.get('eta'),
            }, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
