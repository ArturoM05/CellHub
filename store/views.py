from django.views import View
from django.http import JsonResponse
from .services import CheckoutService
from django.views import View
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render
import json
from .services import OrderService
from .models import Producto, Inventario


class CheckoutView(View):
    """CBV that accepts a POST with JSON body to create an order.

    Expected JSON shape:
    {
      "items": [{"producto_id": 1, "cantidad": 2}, ...]
    }
    """

    def post(self, request):
        try:
            data = json.loads(request.body.decode() or "{}")
        except Exception:
            return HttpResponseBadRequest("Invalid JSON")

        items = data.get("items")
        if items is None:
            return HttpResponseBadRequest("Missing 'items' in request body")

        service = OrderService()
        try:
            orden = service.create_order(request.user, items)
        except Exception as exc:
            return HttpResponseBadRequest(str(exc))

        return JsonResponse({
            "orden_id": orden.id,
            "total": float(orden.total),
            "estado": orden.estado,
        })


class StoreIndexView(View):
    """Main store dashboard: shows products and inventory."""

    def get(self, request):
        productos = list(Producto.objects.all())
        inventarios = {inv.producto_id: inv.stock for inv in Inventario.objects.select_related('producto').all()}
        for p in productos:
            p.stock = inventarios.get(p.id, 0)
        context = {
            'productos': productos,
        }
        return render(request, 'store/index.html', context)
