import os
from store.infra.pagos.mock_pago import MockPago
from store.infra.pagos.real_pago import PagoReal


class ProcesadorPagoFactory:
    @staticmethod
    def crear():
        modo = os.getenv("PAYMENT_MODE", "MOCK")

        if modo == "REAL":
            return PagoReal()

        return MockPago()
