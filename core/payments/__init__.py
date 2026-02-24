"""
core/payments/base.py

Principio OCP: PaymentProcessor es abstracto y cerrado para modificación.
Principio LSP: Cualquier subclase puede reemplazar a PaymentProcessor.
"""
from abc import ABC, abstractmethod


class PaymentProcessor(ABC):
    """Contrato base para todos los procesadores de pago."""

    @abstractmethod
    def process(self, amount: float, data: dict) -> dict:
        """
        Procesa el pago.
        Returns: {'status': 'approved'|'rejected'|'pending', 'transaction_id': str}
        """
        pass

    @abstractmethod
    def validate(self, data: dict) -> bool:
        """Valida que los datos sean suficientes para procesar."""
        pass


# ── Implementaciones concretas ──────────────────────────────────────────────

class CreditCardProcessor(PaymentProcessor):
    """Procesa pagos con tarjeta de crédito."""

    def validate(self, data: dict) -> bool:
        required = ['card_number', 'cvv', 'expiry', 'cardholder_name']
        return all(k in data for k in required)

    def process(self, amount: float, data: dict) -> dict:
        # En producción aquí iría la integración con la pasarela real
        return {
            'status': 'approved',
            'transaction_id': f'CC-{data["card_number"][-4:]}',
            'amount': amount,
            'method': 'credit_card',
        }


class DebitCardProcessor(PaymentProcessor):
    """Procesa pagos con tarjeta débito."""

    def validate(self, data: dict) -> bool:
        return all(k in data for k in ['card_number', 'cvv', 'expiry'])

    def process(self, amount: float, data: dict) -> dict:
        return {
            'status': 'approved',
            'transaction_id': f'DB-{data["card_number"][-4:]}',
            'amount': amount,
            'method': 'debit_card',
        }


class PSEProcessor(PaymentProcessor):
    """Procesa pagos PSE (transferencia bancaria Colombia)."""

    def validate(self, data: dict) -> bool:
        return all(k in data for k in ['bank_code', 'document_type', 'document_number'])

    def process(self, amount: float, data: dict) -> dict:
        return {
            'status': 'pending',
            'transaction_id': f'PSE-{data["bank_code"]}-001',
            'amount': amount,
            'method': 'pse',
            'redirect_url': 'https://pse.com/pay/...',
        }


class NequiProcessor(PaymentProcessor):
    """Procesa pagos Nequi."""

    def validate(self, data: dict) -> bool:
        return 'phone_number' in data

    def process(self, amount: float, data: dict) -> dict:
        return {
            'status': 'pending',
            'transaction_id': f'NQ-{data["phone_number"][-4:]}',
            'amount': amount,
            'method': 'nequi',
        }


class DaviviendaProcessor(PaymentProcessor):
    """Procesa pagos Daviplata / Davivienda."""

    def validate(self, data: dict) -> bool:
        return 'phone_number' in data or 'account_number' in data

    def process(self, amount: float, data: dict) -> dict:
        return {
            'status': 'approved',
            'transaction_id': f'DV-{amount}',
            'amount': amount,
            'method': 'davivienda',
        }
