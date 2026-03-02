"""
seed_data.py — Pobla la base de datos con datos de prueba.

Uso:
    python manage.py shell < seed_data.py
    # o bien:
    python seed_data.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import User
from apps.products.models import Product
from apps.inventory.models import Inventory


def create_users():
    print("👤 Creando usuarios...")
    user, created = User.objects.get_or_create(
        username='juan123',
        defaults={
            'email': 'juan@example.com',
            'first_name': 'Juan',
            'last_name': 'Pérez',
            'phone': '3001234567',
        }
    )
    if created:
        user.set_password('password123')
        user.save()
        print(f"   ✅ Usuario '{user.username}' creado")
    else:
        print(f"   ⏭️  Usuario '{user.username}' ya existe")

    # Admin
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@cellhub.com', 'admin123')
        print("   ✅ Superusuario 'admin' creado")


def create_products():
    print("📱 Creando productos...")
    products = [
        {
            'brand': 'Samsung', 'model_name': 'Galaxy S24 Ultra',
            'price': 4800000, 'ram_gb': 12, 'storage_gb': 256,
            'processor': 'Snapdragon 8 Gen 3', 'battery_mah': 5000,
            'camera_mp': 200, 'screen_inches': 6.8, 'os': 'android',
            'description': 'El flagship más potente de Samsung con cámara de 200MP y S Pen integrado.',
        },
        {
            'brand': 'Samsung', 'model_name': 'Galaxy A55',
            'price': 1800000, 'ram_gb': 8, 'storage_gb': 128,
            'processor': 'Exynos 1480', 'battery_mah': 5000,
            'camera_mp': 50, 'screen_inches': 6.6, 'os': 'android',
            'description': 'Gama media con gran cámara y pantalla AMOLED.',
        },
        {
            'brand': 'Apple', 'model_name': 'iPhone 15 Pro',
            'price': 5200000, 'ram_gb': 8, 'storage_gb': 256,
            'processor': 'Apple A17 Pro', 'battery_mah': 3274,
            'camera_mp': 48, 'screen_inches': 6.1, 'os': 'ios',
            'description': 'iPhone con chip A17 Pro y cámara de 48MP con zoom óptico 3x.',
        },
        {
            'brand': 'Apple', 'model_name': 'iPhone 15',
            'price': 3800000, 'ram_gb': 6, 'storage_gb': 128,
            'processor': 'Apple A16 Bionic', 'battery_mah': 3349,
            'camera_mp': 48, 'screen_inches': 6.1, 'os': 'ios',
            'description': 'iPhone con Dynamic Island y carga USB-C.',
        },
        {
            'brand': 'Xiaomi', 'model_name': 'Redmi Note 13 Pro',
            'price': 1200000, 'ram_gb': 8, 'storage_gb': 256,
            'processor': 'Snapdragon 7s Gen 2', 'battery_mah': 5100,
            'camera_mp': 200, 'screen_inches': 6.67, 'os': 'android',
            'description': 'La mejor relación precio-calidad con cámara de 200MP.',
        },
        {
            'brand': 'Motorola', 'model_name': 'Edge 50 Pro',
            'price': 2100000, 'ram_gb': 12, 'storage_gb': 512,
            'processor': 'Snapdragon 7 Gen 3', 'battery_mah': 4500,
            'camera_mp': 50, 'screen_inches': 6.7, 'os': 'android',
            'description': 'Gama alta de Motorola con carga rápida de 125W.',
        },
    ]

    for data in products:
        product, created = Product.objects.get_or_create(
            brand=data['brand'],
            model_name=data['model_name'],
            defaults=data,
        )
        if created:
            # Crear inventario automáticamente
            Inventory.objects.create(product=product, stock_available=20)
            print(f"   ✅ {product}")
        else:
            print(f"   ⏭️  {product} ya existe")


if __name__ == '__main__':
    print("\n🚀 Iniciando seed de CellHub...\n")
    create_users()
    print()
    create_products()
    print("\n✅ Seed completado!\n")
    print("📌 Credenciales de prueba:")
    print("   Usuario:  juan123 / password123")
    print("   Admin:    admin   / admin123")
    print("\n📖 Documentación API: http://localhost:8000/api/docs/\n")
