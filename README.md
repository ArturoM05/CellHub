# 📱 CellHub — Marketplace de Celulares y Accesorios

Plataforma de e-commerce especializada en venta de celulares y accesorios.

**Stack**: Django 4.2+ | DRF | Celery | Redis | PostgreSQL | Docker Compose | Nginx (API Gateway) | React | Shopify Polaris

**Arquitectura**: Monolito Django + Microservicio Flask (Payments) | Strangler Pattern | Docker Compose en EC2 (AWS Academy)

---

## 🚀 Inicio rápido

### Opción A: Local con Docker Compose (Recomendado)

```bash
# 1. Clonar repositorio
git clone https://github.com/YOUR_USER/cellhub.git
cd cellhub

# 2. Construir y ejecutar servicios
docker compose build
docker compose up -d

# 3. Ver logs
docker compose logs -f django_web

# 4. Acceder a la aplicación
# Frontend: http://localhost/
# API Docs: http://localhost/api/docs/
# Admin: http://localhost/admin/ (usuario: admin, pass: password)
```

### Opción B: Local desarrollo (con venv)

```bash
# 1. Crear entorno virtual
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar migraciones
python manage.py migrate

# 4. Cargar datos de ejemplo
python seed_data.py

# 5. Iniciar servidor
python manage.py runserver

# 6. En otra terminal: iniciar Redis y Celery (si lo necesitas)
docker run -d -p 6379:6379 redis:7-alpine
celery -A config.celery_app worker -l info
```

### Opción C: Desplegar en EC2 (AWS Academy)

Ver [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) para instrucciones detalladas.

**Quick start**:
1. Crear EC2 instance (Ubuntu 22.04 LTS)
2. En "User data": pegar contenido de `user-data.sh`
3. Esperar 3-5 minutos
4. Acceder a `http://EC2_PUBLIC_IP`

---

## 📦 Características principales

### Backend (Django)
- ✅ Catálogo de productos con búsqueda/filtros
- ✅ Gestión de carrito y órdenes
- ✅ Checkout con integración de pagos (microservicio)
- ✅ Notificaciones asíncronas (Celery)
- ✅ Consumo de APIs de terceros (Adapter pattern)
- ✅ i18n (EN/ES con gettext)
- ✅ Auditoría de eventos
- ✅ API REST con OpenAPI/Swagger

### Microservicios
- Flask Payment Service (`/api/v2/payments/`)
- Nginx API Gateway (Strangler Pattern)
- Redis + Celery para tareas asíncronas

### Frontend (React)
- Catálogo responsivo
- Modal de autenticación
- Carrito y checkout
- Shopify Polaris UI components
- i18n (EN/ES)

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────┐
│        Nginx API Gateway (Port 80)      │
├────────┬────────────────────────────────┤
│ /      │ /api/v1/  │ /api/v2/           │
│ (Web)  │ (Django)  │ (Flask)            │
└────────┴───────────┴───────────────────┘
         │           │
    ┌────┴────┐  ┌──┴─────┐
    │  Django │  │ Flask   │
    │  + DRF  │  │ Payments│
    └────┬────┘  └──┬─────┘
         │          │
    ┌────┴──────────┴─────────┐
    │  PostgreSQL Database    │
    │  Redis (Cache/Broker)   │
    │  Celery Worker          │
    └─────────────────────────┘
```

### Patrones de diseño
- **Strangler**: Microservicio Flask reemplaza gradualmente monolito
- **Factory**: `PaymentFactory` para estrategias de pago
- **Builder**: `OrderBuilder` para órdenes complejas
- **Adapter**: Integración con APIs externas
- **DI**: Inyección de dependencias en servicios

---

## 📝 Configuración y desarrollo

### Variables de entorno (.env)

```bash
DEBUG=True                                 # False en producción
SECRET_KEY=tu-clave-secreta-aqui
ALLOWED_HOSTS=localhost,127.0.0.1
CELERY_BROKER_URL=redis://redis:6379/0
DATABASE_URL=sqlite:///db.sqlite3        # O postgresql://...
LANGUAGE_CODE=es-co
```

### Setup de i18n (EN/ES)

```bash
# Generar archivos de traducción
bash i18n-setup.sh

# Editar
locale/en/LC_MESSAGES/django.po
locale/es/LC_MESSAGES/django.po

# Compilar
python manage.py compilemessages
```

### Desarrollo del frontend

```bash
# Terminal 1 — Django API
python manage.py runserver

# Terminal 2 — Vite con hot-reload
cd frontend && npm run dev
```

Abre http://localhost:5173 en desarrollo o http://localhost:8000 en producción.

---

## 🔧 API Endpoints

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
