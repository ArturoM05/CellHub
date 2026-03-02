from django.urls import path
from .views import CartView, CartItemView, CartItemDeleteView
from apps.orders.quick_checkout import AddToCartAPIView, GetCartAPIView, RemoveCartItemAPIView

urlpatterns = [
    path('',                      CartView.as_view(),           name='cart-detail'),
    path('items/',                CartItemView.as_view(),       name='cart-item-add'),
    path('items/<int:item_id>/',  CartItemDeleteView.as_view(), name='cart-item-delete'),
    # Endpoints simples para el frontend
    path('add/',                  AddToCartAPIView.as_view(),   name='cart-add'),
    path('summary/',              GetCartAPIView.as_view(),     name='cart-summary'),
    path('remove/<int:item_id>/', RemoveCartItemAPIView.as_view(), name='cart-remove'),
]
