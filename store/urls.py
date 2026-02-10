from django.urls import path
from .views import CheckoutView, StoreIndexView

urlpatterns = [
    path("", StoreIndexView.as_view(), name="store-index"),
    path("checkout/", CheckoutView.as_view(), name="store-checkout"),
]
from django.urls import path
from .views import CheckoutView

urlpatterns = [
    path("checkout/", CheckoutView.as_view(), name="checkout"),
]
