from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display  = ['username', 'email', 'first_name', 'last_name', 'phone', 'is_staff', 'created_at']
    list_filter   = ['is_staff', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering      = ['-created_at']

    fieldsets = UserAdmin.fieldsets + (
        ('Datos adicionales', {'fields': ('phone',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Datos adicionales', {'fields': ('email', 'first_name', 'last_name', 'phone')}),
    )
