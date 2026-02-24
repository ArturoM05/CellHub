from django.contrib import admin
from .models import Address


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display  = ['user', 'full_name', 'city', 'department', 'street', 'is_default']
    list_filter   = ['city', 'department', 'is_default']
    search_fields = ['user__username', 'full_name', 'city', 'street']
