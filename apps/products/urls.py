from rest_framework.routers import DefaultRouter
from .views import ProductViewSet

router = DefaultRouter()
router.register('', ProductViewSet, basename='products')

urlpatterns = router.urls
# Endpoints generados automáticamente:
#   GET /api/v1/products/              → lista con filtros
#   GET /api/v1/products/{id}/         → detalle
#   GET /api/v1/products/{id}/specs/   → especificaciones
#   GET /api/v1/products/compare/      → comparar modelos
