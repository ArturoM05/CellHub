from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, LoginView, ProfileView
from apps.orders.quick_checkout import GuestLoginView

urlpatterns = [
    path('register/',    RegisterView.as_view(),   name='user-register'),
    path('login/',       LoginView.as_view(),       name='user-login'),
    path('guest-login/', GuestLoginView.as_view(),  name='guest-login'),
    path('refresh/',     TokenRefreshView.as_view(),name='token-refresh'),
    path('profile/',     ProfileView.as_view(),     name='user-profile'),
]
