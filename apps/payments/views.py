"""
apps/payments/views.py

Principio LSP: ProcessPaymentView funciona con CUALQUIER PaymentProcessor.
Principio DIP: Depende de PaymentFactory (abstracción), no de clases concretas.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from core.factories.payment_factory import PaymentFactory
from apps.orders.services import OrderService


class ProcessPaymentView(APIView):
    """POST /api/v1/payments/process/ — Procesa el pago de una orden."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        order_id = request.data.get('order_id')
        payment_data = request.data.get('payment_data', {})

        if not order_id:
            return Response({'error': 'order_id es requerido'}, status=400)

        service = OrderService()
        try:
            result = service.confirm_payment(
                order_id=int(order_id),
                payment_data=payment_data,
            )
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': 'Error procesando el pago'}, status=500)

        return Response(result)


class AvailableMethodsView(APIView):
    """GET /api/v1/payments/methods/ — Lista métodos de pago disponibles."""

    def get(self, request):
        return Response({'methods': PaymentFactory.available_methods()})
