from django.contrib import admin
from django.utils.html import format_html, mark_safe
from django.contrib import messages
from .models import Order, OrderItem, Purchase


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'unit_price', 'subtotal_display']
    fields = ['product', 'quantity', 'unit_price', 'subtotal_display']
    can_delete = False

    def subtotal_display(self, obj):
        subtotal = obj.get_subtotal()
        if subtotal:
            subtotal_str = f'{subtotal:,.0f}'
            return mark_safe(f'<strong>${subtotal_str}</strong>')
        return mark_safe('<strong>-</strong>')
    subtotal_display.short_description = 'Subtotal'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display  = ['order_id', 'user', 'item_count_display', 'total_display',
                     'status_badge', 'payment_method', 'created_at']
    list_filter   = ['status', 'payment_method', 'created_at']
    search_fields = ['user__username', 'user__email', 'transaction_id']
    readonly_fields = ['user', 'shipping_address', 'payment_method', 'total',
                       'transaction_id', 'created_at', 'updated_at']
    ordering  = ['-created_at']
    inlines   = [OrderItemInline]

    fieldsets = (
        ('Informacion de la orden', {
            'fields': ('user', 'status', 'payment_method', 'transaction_id')
        }),
        ('Montos', {
            'fields': ('total',)
        }),
        ('Envio', {
            'fields': ('shipping_address', 'notes')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def order_id(self, obj):
        return format_html('<strong>#{}</strong>', obj.id)
    order_id.short_description = 'Orden'

    def item_count_display(self, obj):
        count = obj.items.count()
        label = 'productos' if count != 1 else 'producto'
        return format_html(
            '<span style="background:#e3f2fd;padding:2px 8px;border-radius:10px;font-size:12px">{} {}</span>',
            count, label
        )
    item_count_display.short_description = 'Productos'

    def total_display(self, obj):
        if obj.total:
            total_str = f'{obj.total:,.0f}'
            return mark_safe(f'<strong style="color:#2e7d32;font-size:14px">${total_str}</strong>')
        return mark_safe('<strong>-</strong>')
    total_display.short_description = 'Total'

    def status_badge(self, obj):
        styles = {
            'pending':   'background:#fff3e0;color:#e65100',
            'confirmed': 'background:#e8f5e9;color:#2e7d32',
            'shipped':   'background:#e3f2fd;color:#1565c0',
            'delivered': 'background:#f3e5f5;color:#6a1b9a',
            'cancelled': 'background:#ffebee;color:#c62828',
        }
        style = styles.get(obj.status, 'background:#eee;color:#333')
        return format_html(
            '<span style="{};padding:3px 10px;border-radius:12px;font-size:11px;font-weight:600">{}</span>',
            style, obj.get_status_display()
        )
    status_badge.short_description = 'Estado'


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display  = ['purchase_id', 'user', 'product_display', 'quantity',
                     'total_display', 'payment_badge', 'status_badge', 'purchased_at']
    list_filter   = ['status', 'payment_method', 'purchased_at', 'product__brand']
    search_fields = ['user__username', 'product__brand', 'product__model_name', 'transaction_id']
    readonly_fields = ['unit_price', 'total', 'status', 'transaction_id', 'purchased_at', 'payment_info']
    ordering  = ['-purchased_at']

    fieldsets = (
        ('Compra rapida', {
            'description': 'Al guardar, el PaymentFactory procesa el pago y descuenta el stock automaticamente.',
            'fields': ('user', 'product', 'quantity', 'payment_method')
        }),
        ('Resultado del pago (automatico)', {
            'fields': ('unit_price', 'total', 'status', 'transaction_id', 'payment_info'),
            'classes': ('collapse',)
        }),
        ('Fecha', {
            'fields': ('purchased_at',),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        try:
            super().save_model(request, obj, form, change)
            self.message_user(
                request,
                'Compra #{} procesada con {}. Estado: {}. Transaction: {}'.format(
                    obj.id, obj.get_payment_method_display(),
                    obj.get_status_display(), obj.transaction_id
                ),
                messages.SUCCESS
            )
        except ValueError as e:
            self.message_user(request, 'Error: {}'.format(e), messages.ERROR)

    def purchase_id(self, obj):
        return format_html('<strong>#{}</strong>', obj.id)
    purchase_id.short_description = 'Compra'

    def product_display(self, obj):
        return format_html(
            '<strong>{} {}</strong><br><small style="color:#999">{} GB RAM &middot; {} GB</small>',
            obj.product.brand, obj.product.model_name,
            obj.product.ram_gb, obj.product.storage_gb
        )
    product_display.short_description = 'Producto'

    def total_display(self, obj):
        total_str = '{:,.0f}'.format(float(obj.total))
        return format_html('<strong style="color:#2e7d32">${}</strong>', total_str)
    total_display.short_description = 'Total'

    def payment_badge(self, obj):
        icons = {
            'credit_card': '💳', 'debit_card': '🏧',
            'pse': '🏦', 'nequi': '📱', 'davivienda': '🔷',
        }
        icon = icons.get(obj.payment_method, '💰')
        return format_html('{} {}', icon, obj.get_payment_method_display())
    payment_badge.short_description = 'Metodo de pago'

    def status_badge(self, obj):
        styles = {
            'approved': 'background:#e8f5e9;color:#2e7d32',
            'pending':  'background:#fff3e0;color:#e65100',
            'rejected': 'background:#ffebee;color:#c62828',
        }
        style = styles.get(obj.status, 'background:#eee;color:#333')
        return format_html(
            '<span style="{};padding:3px 10px;border-radius:12px;font-size:11px;font-weight:600">{}</span>',
            style, obj.get_status_display()
        )
    status_badge.short_description = 'Estado'

    def payment_info(self, obj):
        from core.factories.payment_factory import PaymentFactory
        available = ', '.join(PaymentFactory.available_methods())
        return format_html('<small style="color:#666">Metodos via Factory: {}</small>', available)
    payment_info.short_description = 'Info del Factory'
