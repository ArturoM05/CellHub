"""
flask_payment_service/processors.py

Lógica de negocio de pagos — aislada del monolito Django.
Principio OCP: PaymentProcessor es abstracto; se extiende sin modificar.
Principio LSP: Cualquier subclase puede reemplazar a PaymentProcessor.
"""

from abc import ABC, abstractmethod


class PaymentProcessor(ABC):
    """Contrato base para todos los procesadores de pago."""

    @abstractmethod
    def process(self, amount: float, data: dict) -> dict:
        """
        Procesa el pago.
        Returns: {'status': 'approved'|'rejected'|'pending', 'transaction_id': str, ...}
        """
        pass

    @abstractmethod
    def validate(self, data: dict) -> bool:
        """Valida que los datos sean suficientes para procesar."""
        pass

    def required_fields(self) -> list:
        """Retorna los campos requeridos para este procesador (documentación)."""
        return []


# ── Implementaciones concretas ────────────────────────────────────────────────

class CreditCardProcessor(PaymentProcessor):
    """Procesa pagos con tarjeta de crédito."""

    def required_fields(self):
        return ["card_number", "cvv", "expiry", "cardholder_name"]

    def validate(self, data: dict) -> bool:
        return all(k in data for k in self.required_fields())

    def process(self, amount: float, data: dict) -> dict:
        return {
            "status": "approved",
            "transaction_id": f"CC-{data['card_number'][-4:]}",
            "amount": amount,
            "method": "credit_card",
        }


class DebitCardProcessor(PaymentProcessor):
    """Procesa pagos con tarjeta débito."""

    def required_fields(self):
        return ["card_number", "cvv", "expiry"]

    def validate(self, data: dict) -> bool:
        return all(k in data for k in self.required_fields())

    def process(self, amount: float, data: dict) -> dict:
        return {
            "status": "approved",
            "transaction_id": f"DB-{data['card_number'][-4:]}",
            "amount": amount,
            "method": "debit_card",
        }


class PSEProcessor(PaymentProcessor):
    """Procesa pagos PSE (transferencia bancaria Colombia)."""

    def required_fields(self):
        return ["bank_code", "document_type", "document_number"]

    def validate(self, data: dict) -> bool:
        return all(k in data for k in self.required_fields())

    def process(self, amount: float, data: dict) -> dict:
        return {
            "status": "pending",
            "transaction_id": f"PSE-{data['bank_code']}-001",
            "amount": amount,
            "method": "pse",
            "redirect_url": "https://pse.com/pay/...",
        }


class NequiProcessor(PaymentProcessor):
    """Procesa pagos Nequi."""

    def required_fields(self):
        return ["phone_number"]

    def validate(self, data: dict) -> bool:
        return "phone_number" in data

    def process(self, amount: float, data: dict) -> dict:
        return {
            "status": "pending",
            "transaction_id": f"NQ-{data['phone_number'][-4:]}",
            "amount": amount,
            "method": "nequi",
        }


class DaviviendaProcessor(PaymentProcessor):
    """Procesa pagos Daviplata / Davivienda."""

    def required_fields(self):
        return ["phone_number o account_number"]

    def validate(self, data: dict) -> bool:
        return "phone_number" in data or "account_number" in data

    def process(self, amount: float, data: dict) -> dict:
        return {
            "status": "approved",
            "transaction_id": f"DV-{amount}",
            "amount": amount,
            "method": "davivienda",
        }


# ── Factory ───────────────────────────────────────────────────────────────────

class PaymentFactory:
    """
    Fábrica de procesadores de pago.
    Principio OCP: nuevos métodos se registran sin modificar el factory.
    """

    _processors: dict[str, type[PaymentProcessor]] = {
        "credit_card": CreditCardProcessor,
        "debit_card":  DebitCardProcessor,
        "pse":         PSEProcessor,
        "nequi":       NequiProcessor,
        "davivienda":  DaviviendaProcessor,
    }

    @classmethod
    def get_processor(cls, method: str) -> PaymentProcessor:
        processor_class = cls._processors.get(method)
        if not processor_class:
            available = ", ".join(cls._processors.keys())
            raise ValueError(
                f"Método de pago '{method}' no soportado. Disponibles: {available}"
            )
        return processor_class()

    @classmethod
    def register(cls, method: str, processor_class: type[PaymentProcessor]) -> None:
        if not issubclass(processor_class, PaymentProcessor):
            raise TypeError(f"{processor_class} debe heredar de PaymentProcessor")
        cls._processors[method] = processor_class

    @classmethod
    def available_methods(cls) -> list[str]:
        return list(cls._processors.keys())
