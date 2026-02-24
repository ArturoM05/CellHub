from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


def welcome(request):
    return render(request, 'home.html')


urlpatterns = [
    path('', welcome, name='welcome'),
    path('admin/', admin.site.urls),
    path('api/v1/users/',     include('apps.users.urls')),
    path('api/v1/products/',  include('apps.products.urls')),
    path('api/v1/inventory/', include('apps.inventory.urls')),
    path('api/v1/cart/',      include('apps.cart.urls')),
    path('api/v1/orders/',    include('apps.orders.urls')),
    path('api/v1/payments/',  include('apps.payments.urls')),
    path('api/v1/shipping/',  include('apps.shipping.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/',   SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
