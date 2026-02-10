from django.db import models
from django.contrib.auth.models import User

class Producto(models.Model):
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField()

    ram = models.IntegerField()
    almacenamiento = models.IntegerField()
    procesador = models.CharField(max_length=100)
    camara = models.CharField(max_length=100)
    bateria = models.IntegerField()

    activo = models.BooleanField(default=True)

    def obtener_especificaciones(self):
        return {
            "ram": f"{self.ram} GB",
            "almacenamiento": f"{self.almacenamiento} GB",
            "procesador": self.procesador,
            "camara": self.camara,
            "bateria": f"{self.bateria} mAh",
        }

    def actualizar_precio(self, nuevo_precio):
        if nuevo_precio <= 0:
            raise ValueError("Precio inválido")
        self.precio = nuevo_precio
        self.save()

    def __str__(self):
        return f"{self.marca} {self.modelo}"

class Inventario(models.Model):
    producto = models.OneToOneField(Producto, on_delete=models.CASCADE)
    stock = models.IntegerField()

    def verificar_stock(self, cantidad):
        if cantidad > self.stock:
            raise ValueError(
                f"Stock insuficiente para {self.producto}"
            )

    def descontar_stock(self, cantidad):
        self.verificar_stock(cantidad)
        self.stock -= cantidad
        self.save()

class Orden(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(max_length=30, default="CREADA")
    fecha = models.DateTimeField(auto_now_add=True)

    def calcular_total(self, items):
        self.total = sum(
            item["producto"].precio * item["cantidad"]
            for item in items
        )
