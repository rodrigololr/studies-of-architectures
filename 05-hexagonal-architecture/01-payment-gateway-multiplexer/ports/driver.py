"""
driver.py - Portas Primárias / Inbound (Driver Ports).

Contrato abstrato que define a API dos casos de uso do Core da aplicação.
Adaptadores primários (Controllers HTTP, CLI, Workers) invocam esta porta.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from domain.models import PaymentRequest, PaymentResponse


class ProcessPaymentUseCasePort(ABC):
    @abstractmethod
    def execute(self, request: PaymentRequest) -> PaymentResponse:
        """Processa a cobrança aplicando roteamento inteligente e fallback de gateways."""
        pass
