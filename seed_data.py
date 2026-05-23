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
        'brand': 'Samsung',
        'model_name': 'Galaxy S24 Ultra',
        'price': 4800000,
        'ram_gb': 12,
        'storage_gb': 256,
        'processor': 'Snapdragon 8 Gen 3',
        'battery_mah': 5000,
        'camera_mp': 200,
        'screen_inches': 6.8,
        'os': 'android',
        'image': 'https://www.google.com/url?sa=t&source=web&rct=j&url=https%3A%2F%2Fwww.samsung.com%2Fco%2Fsmartphones%2Fgalaxy-s24-ultra%2F&ved=0CBYQjRxqFwoTCMDWkaC9zpQDFQAAAAAdAAAAABAG&opi=89978449',
        'description': 'El flagship más potente de Samsung con cámara de 200MP y S Pen integrado.',
    },

    {
        'brand': 'Apple',
        'model_name': 'iPhone 15 Pro Max',
        'price': 6200000,
        'ram_gb': 8,
        'storage_gb': 256,
        'processor': 'Apple A17 Pro',
        'battery_mah': 4422,
        'camera_mp': 48,
        'screen_inches': 6.7,
        'os': 'ios',
        'image': 'https://via.placeholder.com/640x360.png?text=iPhone+15+Pro+Max',
        'description': 'Titanio, potencia extrema y excelente batería.',
    },

    {
        'brand': 'Xiaomi',
        'model_name': 'Xiaomi 14',
        'price': 3200000,
        'ram_gb': 12,
        'storage_gb': 512,
        'processor': 'Snapdragon 8 Gen 3',
        'battery_mah': 4610,
        'camera_mp': 50,
        'screen_inches': 6.36,
        'os': 'android',
        'image': 'https://via.placeholder.com/640x360.png?text=Xiaomi+14',
        'description': 'Compacto, potente y con cámaras Leica.',
    },

    {
        'brand': 'Google',
        'model_name': 'Pixel 8 Pro',
        'price': 4100000,
        'ram_gb': 12,
        'storage_gb': 256,
        'processor': 'Google Tensor G3',
        'battery_mah': 5050,
        'camera_mp': 50,
        'screen_inches': 6.7,
        'os': 'android',
        'image': 'https://via.placeholder.com/640x360.png?text=Pixel+8+Pro',
        'description': 'La mejor experiencia Android y fotografía computacional.',
    },

    {
        'brand': 'OnePlus',
        'model_name': 'OnePlus 12',
        'price': 3500000,
        'ram_gb': 16,
        'storage_gb': 512,
        'processor': 'Snapdragon 8 Gen 3',
        'battery_mah': 5400,
        'camera_mp': 50,
        'screen_inches': 6.82,
        'os': 'android',
        'image': 'https://via.placeholder.com/640x360.png?text=OnePlus+12',
        'description': 'Rendimiento brutal y carga ultra rápida.',
    },

    {
        'brand': 'Nothing',
        'model_name': 'Phone 2',
        'price': 2600000,
        'ram_gb': 12,
        'storage_gb': 256,
        'processor': 'Snapdragon 8+ Gen 1',
        'battery_mah': 4700,
        'camera_mp': 50,
        'screen_inches': 6.7,
        'os': 'android',
        'image': 'https://via.placeholder.com/640x360.png?text=Nothing+Phone+2',
        'description': 'Diseño transparente único con Glyph Interface.',
    },

    {
        'brand': 'Motorola',
        'model_name': 'Moto G84',
        'price': 1300000,
        'ram_gb': 8,
        'storage_gb': 256,
        'processor': 'Snapdragon 695',
        'battery_mah': 5000,
        'camera_mp': 50,
        'screen_inches': 6.5,
        'os': 'android',
        'image': 'https://via.placeholder.com/640x360.png?text=Moto+G84',
        'description': 'Excelente autonomía y pantalla OLED.',
    },

    {
        'brand': 'Samsung',
        'model_name': 'Galaxy Z Fold 6',
        'price': 7800000,
        'ram_gb': 12,
        'storage_gb': 512,
        'processor': 'Snapdragon 8 Gen 3',
        'battery_mah': 4400,
        'camera_mp': 50,
        'screen_inches': 7.6,
        'os': 'android',
        'image': 'https://via.placeholder.com/640x360.png?text=Galaxy+Z+Fold+6',
        'description': 'El plegable más avanzado de Samsung.',
    },

    {
        'brand': 'Apple',
        'model_name': 'iPhone SE 2022',
        'price': 2200000,
        'ram_gb': 4,
        'storage_gb': 128,
        'processor': 'Apple A15 Bionic',
        'battery_mah': 2018,
        'camera_mp': 12,
        'screen_inches': 4.7,
        'os': 'ios',
        'image': 'https://via.placeholder.com/640x360.png?text=iPhone+SE+2022',
        'description': 'iPhone compacto y económico.',
    },

    {
        'brand': 'Realme',
        'model_name': 'Realme GT 6',
        'price': 2400000,
        'ram_gb': 12,
        'storage_gb': 256,
        'processor': 'Snapdragon 8s Gen 3',
        'battery_mah': 5500,
        'camera_mp': 50,
        'screen_inches': 6.78,
        'os': 'android',
        'image': 'https://via.placeholder.com/640x360.png?text=Realme+GT+6',
        'description': 'Gran potencia y excelente batería.',
    },
    {
        'brand': 'Motorola',
        'model_name': 'Edge 50 Pro',
        'price': 4200000,
        'ram_gb': 12,
        'storage_gb': 256,
        'processor': 'Snapdragon 8 Gen 2',
        'battery_mah': 4600,
        'camera_mp': 50,
        'screen_inches': 6.7,
        'os': 'android',
        'image': 'https://via.placeholder.com/640x360.png?text=Edge+50+Pro',
        'description': 'Pantalla OLED, carga rápida y muy buenas cámaras.',
    },
    {
        'brand': 'Xiaomi',
        'model_name': 'Redmi Note 13 Pro',
        'price': 1800000,
        'ram_gb': 8,
        'storage_gb': 256,
        'processor': 'Snapdragon 7 Gen 3',
        'battery_mah': 5200,
        'camera_mp': 200,
        'screen_inches': 6.67,
        'os': 'android',
        'image': 'https://via.placeholder.com/640x360.png?text=Redmi+Note+13+Pro',
        'description': 'Gran batería y cámara de alta resolución.',
    },
    {
        'brand': 'Apple',
        'model_name': 'iPhone 15',
        'price': 4900000,
        'ram_gb': 6,
        'storage_gb': 128,
        'processor': 'Apple A16 Bionic',
        'battery_mah': 3340,
        'camera_mp': 48,
        'screen_inches': 6.1,
        'os': 'ios',
        'image': 'https://via.placeholder.com/640x360.png?text=iPhone+15',
        'description': 'Mini diseño, rendimiento sólido y cámara versátil.',
    },
    {
        'brand': 'Apple',
        'model_name': 'iPhone 15 Pro',
        'price': 5800000,
        'ram_gb': 8,
        'storage_gb': 256,
        'processor': 'Apple A17 Pro',
        'battery_mah': 3340,
        'camera_mp': 48,
        'screen_inches': 6.1,
        'os': 'ios',
        'image': 'https://via.placeholder.com/640x360.png?text=iPhone+15+Pro',
        'description': 'Rendimiento pro y materiales premium.',
    },
    {
        'brand': 'Samsung',
        'model_name': 'Galaxy A55',
        'price': 2200000,
        'ram_gb': 8,
        'storage_gb': 256,
        'processor': 'Exynos 1380',
        'battery_mah': 5000,
        'camera_mp': 50,
        'screen_inches': 6.6,
        'os': 'android',
        'image': 'https://via.placeholder.com/640x360.png?text=Galaxy+A55',
        'description': 'Buen balance de precio y características.',
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
            if product.image != data['image']:
                product.image = data['image']
                product.save(update_fields=['image'])
                print(f"   🔄 {product} imagen actualizada")
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
