"""
core/factories/payment_factory.py

Patrón Factory: Centraliza la creación de procesadores de pago.
Principio OCP: Se pueden registrar nuevos métodos sin modificar el factory.
Principio DIP: El cliente depende de la abstracción, no de clases concretas.
"""
from core.payments import (
    PaymentProcessor,
    CreditCardProcessor,
    DebitCardProcessor,
    PSEProcessor,
    NequiProcessor,
    DaviviendaProcessor,
)


class PaymentFactory:
    """
    Fábrica de procesadores de pago.

    Uso:
        processor = PaymentFactory.get_processor('pse')
        result = processor.process(amount=150000, data={...})
    """

    _processors: dict[str, type[PaymentProcessor]] = {
        'credit_card': CreditCardProcessor,
        'debit_card':  DebitCardProcessor,
        'pse':         PSEProcessor,
        'nequi':       NequiProcessor,
        'davivienda':  DaviviendaProcessor,
    }

    @classmethod
    def get_processor(cls, method: str) -> PaymentProcessor:
        """Retorna una instancia del procesador para el método dado."""
        processor_class = cls._processors.get(method)
        if not processor_class:
            available = ', '.join(cls._processors.keys())
            raise ValueError(
                f"Método de pago '{method}' no soportado. "
                f"Disponibles: {available}"
            )
        return processor_class()

    @classmethod
    def register(cls, method: str, processor_class: type[PaymentProcessor]) -> None:
        """
        Registra un nuevo método de pago sin modificar el factory (OCP).

        Uso:
            PaymentFactory.register('bitcoin', BitcoinProcessor)
        """
        if not issubclass(processor_class, PaymentProcessor):
            raise TypeError(f"{processor_class} debe heredar de PaymentProcessor")
        cls._processors[method] = processor_class

    @classmethod
    def available_methods(cls) -> list[str]:
        """Retorna los métodos de pago disponibles."""
        return list(cls._processors.keys())
