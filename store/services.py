from .domain.builders.orden_builder import OrdenBuilder
from .infra.factory.procesador_pago_factory import ProcesadorPagoFactory
from .models import Orden
from store.domain.builders.orden_builder import OrdenBuilder

class OrderService:

    def crear_orden(self, usuario, items):
        builder = OrdenBuilder(usuario)

        for item in items:
            builder.agregar_producto(
                producto_id=item["producto_id"],
                cantidad=item["cantidad"]
            )

        return builder.build()


class PagoService:

    def __init__(self, pago_factory=ProcesadorPagoFactory):
        self.pago_factory = pago_factory

    def procesar_pago(self, orden_id):
        orden = Orden.objects.get(id=orden_id)

        procesador = self.pago_factory.crear()
        resultado = procesador.pagar(orden.total)

        if not resultado:
            raise Exception("Pago rechazado")

        orden.marcar_pagada()
        return orden


class CompraService:
    def __init__(self, procesador_pago):
        self.procesador_pago = procesador_pago

    def ejecutar_proceso_compra(self, usuario, producto, cantidad):
        orden = (
            OrdenBuilder()
            .con_usuario(usuario)
            .agregar_producto(producto, cantidad)
            .calcular_total()
            .build()
        )

        self.procesador_pago.pagar(orden.total)

        orden.save()
        return orden
