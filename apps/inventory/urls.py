from django.urls import path
from .views import StockCheckView

urlpatterns = [
    path('<int:product_id>/stock/', StockCheckView.as_view(), name='stock-check'),
]
