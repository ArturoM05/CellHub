from django.apps import AppConfig

class OrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.orders'

    def ready(self):
        # Personalizar el admin al iniciar
        from django.contrib import admin
        admin.site.site_header = "📱 CellHub Admin"
        admin.site.site_title  = "CellHub"
        admin.site.index_title = "Panel de administración"
