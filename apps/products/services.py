"""
apps/products/services.py

Principio SRP: Lógica de negocio de productos separada de las vistas.
Principio DIP: Las vistas dependen de este servicio, no de los modelos directamente.
"""
from core.builders.product_query_builder import ProductQueryBuilder


class ProductService:
    """
    Servicio que encapsula la lógica de negocio de productos.
    Las vistas delegan aquí en lugar de acceder directamente al ORM.
    """

    def get_filtered_products(self, params: dict):
        """Aplica filtros usando el ProductQueryBuilder."""
        builder = ProductQueryBuilder()

        if params.get('brand'):
            builder.by_brand(params['brand'])

        if params.get('os'):
            builder.by_os(params['os'])

        if params.get('min_price') and params.get('max_price'):
            try:
                builder.by_price_range(
                    float(params['min_price']),
                    float(params['max_price'])
                )
            except (ValueError, TypeError):
                pass

        if params.get('min_ram'):
            try:
                builder.by_ram(int(params['min_ram']))
            except (ValueError, TypeError):
                pass

        if params.get('q'):
            builder.with_search(params['q'])

        if params.get('in_stock'):
            builder.in_stock()

        order = params.get('ordering', '-created_at')
        try:
            builder.ordered_by(order)
        except ValueError:
            builder.ordered_by('-created_at')

        return builder.build()

    def compare_products(self, product_ids: list) -> list:
        """Devuelve especificaciones de varios productos para comparar."""
        from .models import Product
        products = Product.objects.filter(id__in=product_ids, is_active=True)
        return [
            {
                'id': p.id,
                'name': str(p),
                'price': p.price,
                **p.get_specifications()
            }
            for p in products
        ]
