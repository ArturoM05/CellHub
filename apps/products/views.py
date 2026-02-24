"""
apps/products/views.py

Principio SRP: Las vistas solo manejan HTTP. Delegan en ProductService.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import Product
from .serializers import ProductSerializer, ProductSpecsSerializer
from .services import ProductService


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet de productos — solo lectura (catálogo público).

    list:   GET /api/v1/products/          — Listado con filtros
    detail: GET /api/v1/products/{id}/     — Detalle
    specs:  GET /api/v1/products/{id}/specs/ — Especificaciones técnicas
    compare:GET /api/v1/products/compare/  — Comparar modelos
    """
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = ProductService()  # DIP: depende del servicio, no del ORM

    @extend_schema(parameters=[
        OpenApiParameter('q',         str,   description='Búsqueda por nombre/marca'),
        OpenApiParameter('brand',     str,   description='Filtrar por marca'),
        OpenApiParameter('os',        str,   description='android | ios'),
        OpenApiParameter('min_price', float, description='Precio mínimo'),
        OpenApiParameter('max_price', float, description='Precio máximo'),
        OpenApiParameter('min_ram',   int,   description='RAM mínima en GB'),
        OpenApiParameter('in_stock',  bool,  description='Solo productos disponibles'),
        OpenApiParameter('ordering',  str,   description='price | -price | created_at | ram_gb'),
    ])
    def get_queryset(self):
        return self.service.get_filtered_products(self.request.query_params)

    @extend_schema(responses=ProductSpecsSerializer)
    @action(detail=True, methods=['get'], url_path='specs')
    def specs(self, request, pk=None):
        """GET /api/v1/products/{id}/specs/ — Especificaciones técnicas del producto."""
        product = self.get_object()
        return Response({
            'product_name': str(product),
            'price': product.price,
            'specifications': product.get_specifications(),
        })

    @extend_schema(parameters=[
        OpenApiParameter('ids', str, description='IDs separados por coma: 1,2,3')
    ])
    @action(detail=False, methods=['get'], url_path='compare')
    def compare(self, request):
        """GET /api/v1/products/compare/?ids=1,2,3 — Comparar productos."""
        ids_param = request.query_params.get('ids', '')
        try:
            product_ids = [int(i) for i in ids_param.split(',') if i.strip()]
        except ValueError:
            return Response({'error': 'IDs inválidos'}, status=status.HTTP_400_BAD_REQUEST)

        if not product_ids:
            return Response({'error': 'Proporciona al menos un ID'}, status=status.HTTP_400_BAD_REQUEST)

        comparison = self.service.compare_products(product_ids)
        return Response(comparison)
