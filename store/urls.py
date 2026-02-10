from django.urls import path
from store.views import CheckoutView


from .views import (
    StoreIndexView,
    CheckoutView,
    ProcesarPagoView,
    CheckoutHtmlView,
    PagarHtmlView
)

urlpatterns = [
    path("", StoreIndexView.as_view(), name="store-index"),
    path("checkout/", CheckoutView.as_view(), name="checkout"),      # API
    path("comprar/", CheckoutHtmlView.as_view(), name="comprar"),    # HTML
    path("orden/<int:orden_id>/pagar/", PagarHtmlView.as_view(), name="pagar"),
]


urlpatterns = [
    path("", StoreIndexView.as_view(), name="store-index"),
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path("orden/<int:orden_id>/pagar/", ProcesarPagoView.as_view(), name="pagar"),
]
