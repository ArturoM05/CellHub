"""
core/builders/product_query_builder.py

Patrón Builder para construir consultas de productos de forma progresiva.
Permite agregar filtros de manera flexible sin complicar las vistas.
"""
from django.db import models as django_models


class ProductQueryBuilder:
    """
    Builder para consultas de productos.

    Uso:
        products = (ProductQueryBuilder()
            .by_brand('Samsung')
            .by_price_range(500000, 2000000)
            .by_ram(8)
            .with_search('galaxy')
            .ordered_by('-price')
            .build()
        )
    """

    def __init__(self):
        # Import aquí para evitar importaciones circulares
        from apps.products.models import Product
        self._queryset = Product.objects.filter(is_active=True)

    def by_brand(self, brand: str) -> 'ProductQueryBuilder':
        self._queryset = self._queryset.filter(brand__iexact=brand)
        return self

    def by_price_range(self, min_price: float, max_price: float) -> 'ProductQueryBuilder':
        self._queryset = self._queryset.filter(
            price__gte=min_price,
            price__lte=max_price,
        )
        return self

    def by_ram(self, min_ram_gb: int) -> 'ProductQueryBuilder':
        self._queryset = self._queryset.filter(ram_gb__gte=min_ram_gb)
        return self

    def by_os(self, os: str) -> 'ProductQueryBuilder':
        self._queryset = self._queryset.filter(os__iexact=os)
        return self

    def with_search(self, query: str) -> 'ProductQueryBuilder':
        self._queryset = self._queryset.filter(
            django_models.Q(model_name__icontains=query) |
            django_models.Q(brand__icontains=query) |
            django_models.Q(description__icontains=query)
        )
        return self

    def in_stock(self) -> 'ProductQueryBuilder':
        self._queryset = self._queryset.filter(
            inventory__stock_available__gt=0
        )
        return self

    def ordered_by(self, field: str) -> 'ProductQueryBuilder':
        allowed_fields = ['price', '-price', 'created_at', '-created_at', 'brand', 'ram_gb']
        if field not in allowed_fields:
            raise ValueError(f"Campo de orden '{field}' no permitido")
        self._queryset = self._queryset.order_by(field)
        return self

    def build(self):
        return self._queryset
