"""
exceptions.py - Núcleo de Domínio (Domain).
Exceções de negócio para falhas de cobrança e esgotamento de gateways.
"""


class DomainException(Exception):
    pass


class PaymentDomainException(DomainException):
    pass


class AllGatewaysFailedException(PaymentDomainException):
    pass


class InvalidPaymentRequestException(PaymentDomainException):
    pass
