"""apps/inventory/views.py"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from .models import Inventory


class StockCheckView(APIView):
    """GET /api/v1/inventory/{product_id}/stock/"""
    permission_classes = [AllowAny]

    def get(self, request, product_id):
        inventory = get_object_or_404(Inventory, product_id=product_id)
        return Response({
            'product_id': product_id,
            'stock_available': inventory.stock_available,
            'in_stock': inventory.stock_available > 0,
        })
