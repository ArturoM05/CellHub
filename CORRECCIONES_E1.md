# 🔧 Correcciones Entrega 1 — CellHub

**Versión**: 2.0.0  
**Fecha**: Mayo 2026  
**Estado**: ✅ Implementado en Entrega 2

> Este documento evidencia las correcciones y mejoras aplicadas sobre la
> Entrega 1 de acuerdo con el feedback recibido en la sustentación.
> Cumple con el criterio **"Correcciones E1"** de la rúbrica ABET (10 %).

---

## 1. Mejora del Builder Pattern

### Problema indicado por el docente
El `OrderBuilder` original construía la orden de forma plana, sin validaciones
intermedias ni encadenamiento semántico. El `ProductQueryBuilder` tenía métodos
sueltos sin retornar `self`, lo que impedía el encadenamiento fluido típico
del patrón.

### Qué se corrigió

| Aspecto | Antes (E1) | Después (E2) |
|---------|-----------|--------------|
| Encadenamiento | Métodos sin `return self` | Todos los métodos retornan `self` para chaining fluido |
| Validaciones | Sin validaciones en `build()` | `build()` lanza `ValueError` si faltan campos obligatorios |
| Inmutabilidad | Builder reutilizable/mutable | Se limpia el estado interno tras `build()` para evitar reuso accidental |
| Tipado | Sin type hints | Anotaciones completas en todos los métodos públicos |
| Documentación | Sin docstrings | Docstrings con ejemplos de uso en cada método |

### Ejemplo del cambio — `OrderBuilder`

```python
# ── ANTES (E1) ───────────────────────────────────────────────────────────
class OrderBuilder:
    def set_user(self, user):
        self.user = user          # sin return self

    def add_item(self, product, qty, price):
        self.items.append(...)    # sin return self

    def build(self):
        return Order(...)         # sin validación


# ── DESPUÉS (E2) ─────────────────────────────────────────────────────────
class OrderBuilder:
    def set_user(self, user: User) -> "OrderBuilder":
        self._user = user
        return self               # chaining habilitado

    def add_item(self, product: Product, quantity: int, price: Decimal) -> "OrderBuilder":
        if quantity <= 0:
            raise ValueError("La cantidad debe ser mayor a cero.")
        self._items.append({"product": product, "quantity": quantity, "price": price})
        return self

    def build(self) -> Order:
        if not self._user:
            raise ValueError("El builder requiere un usuario antes de construir.")
        if not self._items:
            raise ValueError("La orden debe tener al menos un ítem.")
        order = Order(user=self._user, ...)
        self._reset()             # limpia estado para evitar reuso
        return order

    def _reset(self) -> None:
        self._user = None
        self._items = []
        self._address = None
        self._payment_method = None
```

### Uso mejorado (E2)

```python
# Encadenamiento limpio — imposible en E1
order = (
    OrderBuilder(user=request.user)
    .add_item(product=iphone, quantity=1, price=Decimal("4800000"))
    .set_shipping_address(address)
    .set_payment_method("pse")
    .add_notes("Entregar en portería edificio A")
    .build()
)
```

---

## 2. Mejora del Factory Pattern

### Problema indicado por el docente
El `PaymentFactory` original usaba un `if/elif` largo que violaba el Principio
Abierto/Cerrado (OCP). Agregar un nuevo medio de pago requería modificar el
factory directamente. Además no había manejo de métodos desconocidos.

### Qué se corrigió

| Aspecto | Antes (E1) | Después (E2) |
|---------|-----------|--------------|
| Registro de procesadores | `if/elif` hardcodeado | Diccionario `_registry` dinámico |
| OCP | Violado — modificar factory para agregar procesador | Cumplido — `register()` agrega sin tocar el factory |
| Error handling | Sin manejo de método desconocido | `ValueError` descriptivo si el método no está registrado |
| Extensibilidad | Solo métodos en el código fuente | `register()` permite inyectar procesadores externos en runtime |
| Testing | Difícil mockear | Registry reemplazable en tests |

### Ejemplo del cambio — `PaymentFactory`

```python
# ── ANTES (E1) ───────────────────────────────────────────────────────────
class PaymentFactory:
    @staticmethod
    def get_processor(method: str):
        if method == "credit_card":
            return CreditCardProcessor()
        elif method == "pse":
            return PSEProcessor()
        elif method == "cash":
            return CashProcessor()
        # ← agregar un nuevo método requiere editar este bloque


# ── DESPUÉS (E2) ─────────────────────────────────────────────────────────
class PaymentFactory:
    _registry: dict[str, type] = {
        "credit_card": CreditCardProcessor,
        "pse":         PSEProcessor,
        "cash":        CashProcessor,
        "nequi":       NequiProcessor,   # nuevo método — cero cambios al factory
    }

    @classmethod
    def get_processor(cls, method: str) -> PaymentProcessor:
        processor_class = cls._registry.get(method)
        if not processor_class:
            available = ", ".join(cls._registry.keys())
            raise ValueError(
                f"Método de pago '{method}' no registrado. "
                f"Disponibles: {available}"
            )
        return processor_class()

    @classmethod
    def register(cls, method: str, processor_class: type) -> None:
        """Registra un nuevo procesador sin modificar el factory (OCP)."""
        if not issubclass(processor_class, PaymentProcessor):
            raise TypeError("El procesador debe heredar de PaymentProcessor.")
        cls._registry[method] = processor_class
```

### Agregar un nuevo medio de pago (E2) — sin tocar el factory

```python
# En cualquier módulo externo, sin abrir core/factories/payment_factory.py:
from core.factories.payment_factory import PaymentFactory

class DaviPlataProcessor(PaymentProcessor):
    def process(self, amount, data):
        ...

PaymentFactory.register("daviplata", DaviPlataProcessor)
processor = PaymentFactory.get_processor("daviplata")
```

---

## 3. Mejora de la Interfaz (UI/UX)

### Problema indicado por el docente
La interfaz de E1 mostraba poca información del producto, sin especificaciones
técnicas visibles, sin comparación de productos y con formularios básicos sin
validación en tiempo real.

### Qué se corrigió

| Área | Antes (E1) | Después (E2) |
|------|-----------|--------------|
| Ficha de producto | Solo nombre, precio e imagen | + specs técnicas (RAM, almacenamiento, SO, cámara) |
| Comparación | No existía | Endpoint `GET /api/v1/products/compare/?ids=1,2,3` + UI de comparación |
| Formularios | Sin validación client-side | Validación en tiempo real con mensajes descriptivos |
| Carrito | Lista simple | Subtotales por ítem, total con IVA, botón de eliminar |
| Responsive | Parcial | Probado en mobile, tablet y desktop |
| Accesibilidad | Sin atributos ARIA | Labels, roles y aria-describedby en formularios críticos |

---

## 4. Ampliación del Seed Data

### Problema indicado por el docente
El seed de E1 tenía 3–4 productos y 2 usuarios, insuficiente para demostrar
filtros, búsqueda y comparación de productos.

### Qué se corrigió

| Entidad | E1 | E2 |
|---------|----|----|
| Usuarios | 2 | 10 (admin + 9 clientes con perfiles distintos) |
| Productos | 4 | 25 (5 marcas × 5 gamas: alta, media-alta, media, baja, accesorios) |
| Categorías | 1 | 4 (smartphones, tablets, accesorios, wearables) |
| Órdenes demo | 0 | 8 órdenes con distintos estados (pending, confirmed, shipped, delivered) |
| Reseñas | 0 | 15 reseñas distribuidas en productos populares |
| Direcciones | 0 | 5 direcciones de envío de ejemplo |

```bash
# Ejecutar el seed actualizado
python seed_data.py

# Verificar conteo
python manage.py shell -c "
from apps.products.models import Product
from apps.users.models import User
from apps.orders.models import Order
print(f'Productos: {Product.objects.count()}')
print(f'Usuarios:  {User.objects.count()}')
print(f'Órdenes:   {Order.objects.count()}')
"
```

---

## 5. Resumen de archivos modificados en E2 por estas correcciones

```
core/
├── builders/
│   ├── order_builder.py          ← refactorizado (chaining + validaciones)
│   └── product_query_builder.py  ← refactorizado (return self en todos los métodos)
├── factories/
│   └── payment_factory.py        ← refactorizado (registry dinámico + OCP)
└── payments/
    └── processors.py             ← agregado NequiProcessor como ejemplo OCP

frontend/src/
├── components/
│   ├── ProductCard.jsx           ← más información visible
│   ├── ProductCompare.jsx        ← componente nuevo
│   └── CartSummary.jsx           ← subtotales + IVA
└── pages/
    └── ProductDetail.jsx         ← specs técnicas completas

seed_data.py                      ← 25 productos, 10 usuarios, 8 órdenes
```

---

## ✅ Checklist de verificación

- [x] Builder con encadenamiento fluido (`return self` en todos los métodos)
- [x] Builder con validaciones en `build()`
- [x] Factory con registro dinámico (sin `if/elif`)
- [x] Factory cumple OCP — nuevo procesador sin modificar el factory
- [x] Interfaz muestra specs técnicas en ficha de producto
- [x] Comparación de productos implementada
- [x] Formularios con validación en tiempo real
- [x] Seed con mínimo 20 productos y 8 órdenes demo
- [x] Documentado en este archivo para evidencia en sustentación

---

**Versión**: 2.0.0  
**Última actualización**: Mayo 2026  
**Aplica a**: Entrega 2 — Arquitectura & Deployment
