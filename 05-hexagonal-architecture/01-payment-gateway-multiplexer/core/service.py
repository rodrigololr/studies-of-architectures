"""
service.py - Núcleo da Aplicação (Core / Application Service).

Implementa a Driver Port `ProcessPaymentUseCasePort` e orquestra a lógica
de chaveamento inteligente e fallback de gateways usando as Driven Ports.
NÃO possui nenhuma dependência de bibliotecas ou SDKs de terceiros.
"""

from __future__ import annotations
from typing import List
from domain.models import PaymentRequest, PaymentResponse, PaymentStatus
from domain.exceptions import AllGatewaysFailedException, InvalidPaymentRequestException
from ports.driver import ProcessPaymentUseCasePort
from ports.driven import PaymentGatewayPort, PaymentAuditRepositoryPort


class PaymentMultiplexerService(ProcessPaymentUseCasePort):
    def __init__(
        self,
        gateways_in_priority_order: List[PaymentGatewayPort],
        audit_repository: PaymentAuditRepositoryPort,
    ) -> None:
        self.gateways = gateways_in_priority_order
        self.audit_repository = audit_repository

    def execute(self, request: PaymentRequest) -> PaymentResponse:
        # 1. Validação de Regras de Domínio
        if request.amount <= 0:
            raise InvalidPaymentRequestException("O valor da cobrança deve ser estritamente positivo.")

        if not request.customer_email or "@" not in request.customer_email:
            raise InvalidPaymentRequestException("E-mail do pagador inválido para emissão de comprovante.")

        # 2. Orquestração com Fallback entre Gateways disponíveis
        attempt_errors: List[str] = []

        for gateway in self.gateways:
            if not gateway.is_available:
                attempt_errors.append(f"{gateway.provider_name}: Indisponível (Healthcheck em falha)")
                continue

            try:
                response = gateway.charge(request)
                if response.status == PaymentStatus.AUTHORIZED:
                    # Sucesso no gateway atual -> Grava auditoria e retorna imediatamente
                    self.audit_repository.save_audit(response)
                    return response
                else:
                    attempt_errors.append(f"{gateway.provider_name}: {response.error_message}")
            except Exception as ex:
                attempt_errors.append(f"{gateway.provider_name}: Exceção inesperada ({ex})")

        # 3. Todos os gateways falharam
        all_errors_msg = " | ".join(attempt_errors)
        raise AllGatewaysFailedException(
            f"Todos os provedores de pagamento falharam ao processar o pedido {request.payment_id}. "
            f"Detalhes: [{all_errors_msg}]"
        )
