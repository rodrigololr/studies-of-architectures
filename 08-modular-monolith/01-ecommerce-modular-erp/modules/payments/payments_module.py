"""Ponto de Entrada e Facade do Módulo Payments."""

import uuid
from datetime import datetime
from shared.events import InProcessEventBus
from modules.payments.public_contracts import (
    IPaymentsModule,
    ProcessPaymentCommand,
    PaymentResultDto,
    PaymentSucceededDomainEvent,
    PaymentFailedDomainEvent,
)
from modules.payments.internal.payments_internal import (
    _InternalPaymentTransaction,
    _InternalPaymentRepository,
)


class PaymentsModule(IPaymentsModule):
    """Facade pública do módulo Payments."""
    def __init__(self, event_bus: InProcessEventBus) -> None:
        self._repo = _InternalPaymentRepository()
        self._bus = event_bus

    def process_payment(self, cmd: ProcessPaymentCommand) -> PaymentResultDto:
        tx_id = f"TX_{uuid.uuid4().hex[:8].upper()}"

        # Regra de negócio de simulação de autorização
        # Se valor for exatamente 99999.0 ou email contiver 'recusado', simula rejeição
        if cmd.amount >= 50000.0 or "recusado" in cmd.customer_email.lower():
            tx = _InternalPaymentTransaction(
                transaction_id=tx_id,
                order_id=cmd.order_id,
                customer_email=cmd.customer_email,
                amount=cmd.amount,
                payment_method=cmd.payment_method,
                status="DECLINED",
                auth_code=None,
                created_at=datetime.now(),
            )
            self._repo.save(tx)

            # Publica evento de falha no barramento intra-processo
            self._bus.publish(PaymentFailedDomainEvent(
                order_id=cmd.order_id,
                reason="Transação não autorizada pela emissora do cartão.",
            ))

            return PaymentResultDto(
                transaction_id=tx_id,
                order_id=cmd.order_id,
                is_successful=False,
                error_message="Cartão recusado pela operadora (Saldo insuficiente ou suspeita de fraude).",
            )

        # Pagamento aprovado
        auth_code = f"AUTH_{uuid.uuid4().hex[:6].upper()}"
        tx = _InternalPaymentTransaction(
            transaction_id=tx_id,
            order_id=cmd.order_id,
            customer_email=cmd.customer_email,
            amount=cmd.amount,
            payment_method=cmd.payment_method,
            status="APPROVED",
            auth_code=auth_code,
            created_at=datetime.now(),
        )
        self._repo.save(tx)

        # Publica evento de sucesso
        self._bus.publish(PaymentSucceededDomainEvent(
            order_id=cmd.order_id,
            transaction_id=tx_id,
            amount=cmd.amount,
        ))

        return PaymentResultDto(
            transaction_id=tx_id,
            order_id=cmd.order_id,
            is_successful=True,
            auth_code=auth_code,
        )
