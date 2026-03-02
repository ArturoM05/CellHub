from django.urls import path
from .views import ProcessPaymentView, AvailableMethodsView

urlpatterns = [
    path('process/', ProcessPaymentView.as_view(), name='payment-process'),
    path('methods/', AvailableMethodsView.as_view(), name='payment-methods'),
]
