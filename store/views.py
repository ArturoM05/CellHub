from django.views import View
from django.shortcuts import render
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponse
from store.models import Producto, Orden, OrdenItem
from store.services import CompraService, PagoService, OrderService
from django.http import JsonResponse, HttpResponseBadRequest
from store.infra.factory.procesador_pago_factory import ProcesadorPagoFactory

class StoreIndexView(View):

    def get(self, request):
        productos = Producto.objects.all()
        return render(request, "store/index.html", {"productos": productos})


class CheckoutView(View):
    def post(self, request):
        producto_id = request.POST.get("producto_id")
        cantidad = int(request.POST.get("cantidad", 1))

        producto = get_object_or_404(Producto, id=producto_id)

        procesador_pago = ProcesadorPagoFactory.crear()
        service = CompraService(procesador_pago)

        orden = service.ejecutar_proceso_compra(
            usuario=request.user,
            producto=producto,
            cantidad=cantidad
        )

        return HttpResponse(f"✅ Compra realizada. Orden #{orden.id}")


class ProcesarPagoView(View):

    def post(self, request, orden_id):
        try:
            orden = PagoService().procesar_pago(orden_id)
        except Exception as e:
            return HttpResponseBadRequest(str(e))

        return JsonResponse({"estado": orden.estado})


class CheckoutHtmlView(View):

    def post(self, request):
        producto_id = request.POST.get("producto_id")
        cantidad = int(request.POST.get("cantidad", 1))

        items = [{
            "producto_id": producto_id,
            "cantidad": cantidad
        }]

        orden = OrderService().crear_orden(request.user, items)
        return redirect("pagar", orden_id=orden.id)
    
class PagarHtmlView(View):

    def get(self, request, orden_id):
        orden = get_object_or_404(Orden, id=orden_id)
        return render(request, "store/checkout.html", {"orden": orden})

    def post(self, request, orden_id):
        PagoService().procesar_pago(orden_id)
        return render(request, "store/success.html")

