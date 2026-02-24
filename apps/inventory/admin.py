from django.contrib import admin
from django.utils.html import format_html
from .models import Inventory


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display  = ['product', 'stock_bar', 'stock_available', 'stock_reserved', 'updated_at']
    search_fields = ['product__brand', 'product__model_name']
    ordering      = ['stock_available']
    readonly_fields = ['updated_at']

    def stock_bar(self, obj):
        pct = min(100, int((obj.stock_available / 30) * 100))
        color = '#28a745' if pct > 30 else '#ffc107' if pct > 0 else '#dc3545'
        return format_html(
            '<div style="width:100px;background:#eee;border-radius:4px;height:12px">'
            '<div style="width:{}%;background:{};border-radius:4px;height:12px"></div></div>',
            pct, color
        )
    stock_bar.short_description = 'Disponibilidad'
