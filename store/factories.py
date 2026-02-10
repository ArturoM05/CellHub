from .pagos import PagoTarjeta, PagoPSE

class PagoFactory:

    @staticmethod
    def crear(metodo_pago):
        if metodo_pago == "tarjeta":
            return PagoTarjeta()
        elif metodo_pago == "pse":
            return PagoPSE()
        else:
            raise ValueError("Método de pago no soportado")
