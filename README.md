# 📱 CellHub — Marketplace de Celulares

Django + Django REST Framework | SOLID + Factory + Builder

---

## 🚀 Configuración inicial

```bash
# 1. Crear entorno virtual
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Crear migraciones y base de datos
python manage.py makemigrations users
python manage.py makemigrations products
python manage.py makemigrations inventory
python manage.py makemigrations cart
python manage.py makemigrations orders
python manage.py makemigrations payments
python manage.py makemigrations shipping
python manage.py migrate

# 4. Cargar datos de prueba
python seed_data.py

# 5. Correr servidor
python manage.py runserver
```

---

## 📖 Documentación API

Abre en tu navegador: **http://localhost:8000/api/docs/**

(Swagger UI generado automáticamente con drf-spectacular)

---

## 🔑 Autenticación

```bash
# Login — obtener token JWT
POST http://localhost:8000/api/v1/users/login/
{
  "username": "juan123",
  "password": "password123"
}

# Respuesta:
{
  "access": "eyJ...",   <-- usar en Authorization: Bearer <token>
  "refresh": "eyJ..."
}
```

---

## 📡 Endpoints principales

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | /api/v1/users/register/ | Registro |
| POST | /api/v1/users/login/ | Login → JWT |
| GET | /api/v1/products/ | Catálogo (con filtros) |
| GET | /api/v1/products/{id}/specs/ | Especificaciones técnicas |
| GET | /api/v1/products/compare/?ids=1,2 | Comparar productos |
| GET | /api/v1/inventory/{id}/stock/ | Verificar stock |
| GET | /api/v1/cart/ | Ver carrito |
| POST | /api/v1/cart/items/ | Agregar al carrito |
| POST | /api/v1/orders/create/ | Crear orden (Builder) |
| POST | /api/v1/payments/process/ | Procesar pago (Factory) |

### Filtros de productos

```
GET /api/v1/products/?brand=Samsung
GET /api/v1/products/?os=ios
GET /api/v1/products/?min_price=1000000&max_price=3000000
GET /api/v1/products/?min_ram=8
GET /api/v1/products/?q=galaxy&ordering=-price
GET /api/v1/products/?in_stock=true
```

---

## 🏗️ Patrones de diseño implementados

### Factory Pattern
```python
# core/factories/payment_factory.py
processor = PaymentFactory.get_processor('pse')
result = processor.process(amount=150000, data={...})

# Agregar nuevo método SIN modificar el factory (OCP):
PaymentFactory.register('bitcoin', BitcoinProcessor)
```

### Builder Pattern
```python
# core/builders/order_builder.py
order = (OrderBuilder(user=request.user)
    .add_item(product, quantity=1, price=4800000)
    .set_shipping_address(address)
    .set_payment_method('credit_card')
    .add_notes('Entregar en portería')
    .build()
)

# core/builders/product_query_builder.py
products = (ProductQueryBuilder()
    .by_brand('Samsung')
    .by_price_range(1000000, 5000000)
    .by_ram(8)
    .ordered_by('-price')
    .build()
)
```

---

## 📂 Estructura del proyecto

```
cellhub/
├── config/           ← Settings, URLs, WSGI
├── core/
│   ├── factories/    ← PaymentFactory
│   ├── builders/     ← OrderBuilder, ProductQueryBuilder
│   ├── notifications/← EmailNotifier, SMSNotifier (ISP)
│   └── payments/     ← PaymentProcessor base + implementaciones (OCP)
├── apps/
│   ├── users/        ← Registro, login, perfil (JWT)
│   ├── products/     ← Catálogo, specs, comparación
│   ├── inventory/    ← Stock
│   ├── cart/         ← Carrito de compras
│   ├── orders/       ← Órdenes (usa OrderBuilder)
│   ├── payments/     ← Pagos (usa PaymentFactory)
│   └── shipping/     ← Direcciones
├── seed_data.py      ← Datos de prueba
└── manage.py
```
