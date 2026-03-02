from django.urls import path
from .views import OrderListCreateView, CreateOrderView, OrderDetailView, ChangeOrderStatusView
from .quick_checkout import QuickCheckoutView

urlpatterns = [
    path('',                  OrderListCreateView.as_view(),  name='order-list'),
    path('create/',           CreateOrderView.as_view(),      name='order-create'),
    path('<int:pk>/',         OrderDetailView.as_view(),      name='order-detail'),
    path('<int:pk>/status/',  ChangeOrderStatusView.as_view(),name='order-status'),
    path('quick-checkout/',   QuickCheckoutView.as_view(),    name='quick-checkout'),
]
