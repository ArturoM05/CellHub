from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from .models import Producto, Inventario, Orden
from .services import OrderService

User = get_user_model()


class OrderServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="pwd")
        p1 = Producto.objects.create(marca="A", modelo="X", precio=100, descripcion="", ram=4, almacenamiento=64, procesador="p", camara="c", bateria=3000)
        p2 = Producto.objects.create(marca="B", modelo="Y", precio=200, descripcion="", ram=8, almacenamiento=128, procesador="p2", camara="c2", bateria=4000)
        Inventario.objects.create(producto=p1, stock=10)
        Inventario.objects.create(producto=p2, stock=5)

    def test_create_order_reduces_stock_and_creates_order(self):
        items = [{"producto_id": Producto.objects.first().id, "cantidad": 2}]
        service = OrderService(notifier_kind="console")
        order = service.create_order(self.user, items)
        self.assertIsInstance(order, Orden)
        self.assertEqual(order.total, Producto.objects.first().precio * 2)
        inv = Inventario.objects.get(producto=Producto.objects.first())
        self.assertEqual(inv.stock, 8)


class CheckoutViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="tester2", password="pwd")
        p = Producto.objects.create(marca="C", modelo="Z", precio=50, descripcion="", ram=2, almacenamiento=32, procesador="p3", camara="c3", bateria=2500)
        Inventario.objects.create(producto=p, stock=3)

    def test_checkout_view_creates_order(self):
        self.client.force_login(self.user)
        p = Producto.objects.first()
        resp = self.client.post(
            "/store/checkout/",
            data='{"items":[{"producto_id":%d,"cantidad":1}]}' % p.id,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("orden_id", data)
        self.assertEqual(float(data["total"]), float(p.precio))
