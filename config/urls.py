from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from core.views import system_info


def welcome(request):
    return render(request, 'home.html')


# API routes (language-independent for API consumption)
api_patterns = [
    path('api/v1/system/info/', system_info, name='system-info'),
    path('api/v1/users/',     include('apps.users.urls')),
    path('api/v1/products/',  include('apps.products.urls')),
    path('api/v1/inventory/', include('apps.inventory.urls')),
    path('api/v1/cart/',      include('apps.cart.urls')),
    path('api/v1/orders/',    include('apps.orders.urls')),
    path('api/v1/payments/',  include('apps.payments.urls')),
    path('api/v1/shipping/',  include('apps.shipping.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/',   SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

# i18n patterns (for web routes)
urlpatterns = i18n_patterns(
    path('', welcome, name='welcome'),
    path('admin/', admin.site.urls),
) + api_patterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
