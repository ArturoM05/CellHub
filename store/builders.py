from .models import Orden, Inventario

class OrdenBuilder:

    def __init__(self):
        self.usuario = None
        self.items = []

    def para_usuario(self, usuario):
        self.usuario = usuario
        return self

    def agregar_producto(self, producto, cantidad):
        inventario = Inventario.objects.get(producto=producto)
        inventario.verificar_stock(cantidad)

        self.items.append({
            "producto": producto,
            "cantidad": cantidad
        })

        return self

    def build(self):
        if not self.usuario:
            raise ValueError("La orden debe tener usuario")

        orden = Orden(usuario=self.usuario)
        orden.calcular_total(self.items)
        orden.save()

        for item in self.items:
            inventario = Inventario.objects.get(
                producto=item["producto"]
            )
            inventario.descontar_stock(item["cantidad"])

        return orden
