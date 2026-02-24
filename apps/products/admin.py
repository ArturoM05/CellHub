from django.contrib import admin
from django.utils.html import format_html, mark_safe
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'colored_brand', 'model_name', 'os_badge',
        'ram_gb', 'storage_gb', 'formatted_price', 'stock_display', 'is_active'
    ]
    list_filter   = ['brand', 'os', 'is_active', 'ram_gb']
    search_fields = ['brand', 'model_name', 'processor']
    list_editable = ['is_active']
    ordering      = ['-created_at']

    fieldsets = (
        ('Informacion general', {
            'fields': ('brand', 'model_name', 'price', 'description', 'image', 'is_active')
        }),
        ('Especificaciones tecnicas', {
            'fields': (
                ('ram_gb', 'storage_gb'),
                ('processor', 'os'),
                ('camera_mp', 'battery_mah', 'screen_inches'),
            )
        }),
    )

    def colored_brand(self, obj):
        colors = {
            'Samsung': '#1428A0', 'Apple': '#555555',
            'Xiaomi': '#FF6900', 'Motorola': '#005A9C',
        }
        color = colors.get(obj.brand, '#6c63ff')
        return format_html('<span style="color:{};font-weight:700">{}</span>', color, obj.brand)
    colored_brand.short_description = 'Marca'

    def os_badge(self, obj):
        if obj.os == 'ios':
            return mark_safe('<span style="background:#000;color:#fff;padding:2px 8px;border-radius:10px;font-size:11px">iOS</span>')
        return mark_safe('<span style="background:#3DDC84;color:#000;padding:2px 8px;border-radius:10px;font-size:11px">Android</span>')
    os_badge.short_description = 'OS'

    def formatted_price(self, obj):
        if obj.price:
            price_str = f"${obj.price:,.0f}"
            return mark_safe(f'<strong>{price_str}</strong>')
        return mark_safe('<strong>-</strong>')
    formatted_price.short_description = 'Precio'

    def stock_display(self, obj):
        try:
            stock = obj.inventory.stock_available
            color = '#28a745' if stock > 5 else '#ffc107' if stock > 0 else '#dc3545'
            return format_html('<span style="color:{};font-weight:600">{} unid.</span>', color, stock)
        except Exception:
            return mark_safe('<span style="color:#dc3545">Sin inventario</span>')
    stock_display.short_description = 'Stock'
