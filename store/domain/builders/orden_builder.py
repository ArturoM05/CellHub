from store.models import Orden, OrdenItem


class OrdenBuilder:
    def __init__(self):
        self._usuario = None
        self._items = []
        self._total = 0

    def con_usuario(self, usuario):
        self._usuario = usuario
        return self

    def agregar_producto(self, producto, cantidad):
        self._items.append((producto, cantidad))
        return self

    def calcular_total(self):
        self._total = sum(
            producto.precio * cantidad
            for producto, cantidad in self._items
        )
        return self

    def build(self):
        if not self._usuario:
            raise ValueError("Usuario requerido")

        orden = Orden(usuario=self._usuario, total=self._total)
        orden.save()

        for producto, cantidad in self._items:
            OrdenItem.objects.create(
                orden=orden,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=producto.precio
            )

        return orden
