"""Order Saga Orchestrator: Máquina de estados para transações distribuídas."""

import uuid
from typing import List, Optional
from saga.saga_models import (
    OrderDetails,
    SagaStep,
    SagaStatus,
    SagaExecutionLog,
    SagaResult,
)
from services.order_service import OrderService
from services.payment_service import PaymentService
from services.inventory_service import InventoryService
from services.delivery_service import DeliveryService


class OrderSagaOrchestrator:
    """Orquestrador central de Saga para checkout em microsserviços."""

    def __init__(
        self,
        order_svc: OrderService,
        payment_svc: PaymentService,
        inventory_svc: InventoryService,
        delivery_svc: DeliveryService,
    ) -> None:
        self._order = order_svc
        self._payment = payment_svc
        self._inventory = inventory_svc
        self._delivery = delivery_svc

    def execute_order_saga(self, order: OrderDetails) -> SagaResult:
        saga_id = f"SAGA-{uuid.uuid4().hex[:8].upper()}"
        history: List[SagaExecutionLog] = []

        payment_id: Optional[str] = None
        reservation_id: Optional[str] = None
        dispatch_id: Optional[str] = None

        # ---------------------------------------------------------------------
        # ETAPA 1: Criar Pedido PENDENTE no OrderService
        # ---------------------------------------------------------------------
        self._order.create_pending_order(order.order_id, order.customer_id, order.total_amount)
        history.append(
            SagaExecutionLog(
                step=SagaStep.CREATE_ORDER,
                action="FORWARD",
                status="SUCCESS",
                details=f"Pedido {order.order_id} criado no estado PENDING.",
            )
        )

        # ---------------------------------------------------------------------
        # ETAPA 2: Autorizar Pagamento no PaymentService
        # ---------------------------------------------------------------------
        pay_ok, pay_res = self._payment.process_charge(
            order.order_id, order.customer_id, order.total_amount
        )
        if not pay_ok:
            history.append(
                SagaExecutionLog(
                    step=SagaStep.PROCESS_PAYMENT,
                    action="FORWARD",
                    status="FAILURE",
                    details=f"Falha no pagamento: {pay_res}",
                )
            )
            # Compensação da Etapa 1
            self._compensate_order(order.order_id, pay_res, history)
            return SagaResult(
                saga_id=saga_id,
                order_id=order.order_id,
                final_status=SagaStatus.COMPENSATED,
                history=history,
                failure_reason=pay_res,
            )

        payment_id = pay_res
        history.append(
            SagaExecutionLog(
                step=SagaStep.PROCESS_PAYMENT,
                action="FORWARD",
                status="SUCCESS",
                details=f"Pagamento capturado com sucesso (ID: {payment_id}).",
            )
        )

        # ---------------------------------------------------------------------
        # ETAPA 3: Reservar Estoque no InventoryService
        # ---------------------------------------------------------------------
        inv_ok, inv_res = self._inventory.reserve_inventory(order.order_id, order.items)
        if not inv_ok:
            history.append(
                SagaExecutionLog(
                    step=SagaStep.RESERVE_INVENTORY,
                    action="FORWARD",
                    status="FAILURE",
                    details=f"Falha de estoque: {inv_res}",
                )
            )
            # Compensação em cascata reversa: Estornar Pagamento -> Cancelar Pedido
            self._compensate_payment(payment_id, history)
            self._compensate_order(order.order_id, inv_res, history)
            return SagaResult(
                saga_id=saga_id,
                order_id=order.order_id,
                final_status=SagaStatus.COMPENSATED,
                history=history,
                failure_reason=inv_res,
            )

        reservation_id = inv_res
        history.append(
            SagaExecutionLog(
                step=SagaStep.RESERVE_INVENTORY,
                action="FORWARD",
                status="SUCCESS",
                details=f"Itens reservados com sucesso (ID: {reservation_id}).",
            )
        )

        # ---------------------------------------------------------------------
        # ETAPA 4: Agendar Entrega no DeliveryService
        # ---------------------------------------------------------------------
        deliv_ok, deliv_res = self._delivery.schedule_delivery(
            order.order_id, order.shipping_postal_code
        )
        if not deliv_ok:
            history.append(
                SagaExecutionLog(
                    step=SagaStep.SCHEDULE_DELIVERY,
                    action="FORWARD",
                    status="FAILURE",
                    details=f"Falha no agendamento logístico: {deliv_res}",
                )
            )
            # Compensação em cascata reversa: Devolver Estoque -> Estornar Pagamento -> Cancelar Pedido
            self._compensate_inventory(reservation_id, history)
            self._compensate_payment(payment_id, history)
            self._compensate_order(order.order_id, deliv_res, history)
            return SagaResult(
                saga_id=saga_id,
                order_id=order.order_id,
                final_status=SagaStatus.COMPENSATED,
                history=history,
                failure_reason=deliv_res,
            )

        dispatch_id = deliv_res
        history.append(
            SagaExecutionLog(
                step=SagaStep.SCHEDULE_DELIVERY,
                action="FORWARD",
                status="SUCCESS",
                details=f"Despacho agendado (Tracking: {dispatch_id}).",
            )
        )

        # ---------------------------------------------------------------------
        # CONCLUSÃO DE SUCESSO: Confirmar Pedido
        # ---------------------------------------------------------------------
        self._order.confirm_order(order.order_id)
        history.append(
            SagaExecutionLog(
                step=SagaStep.CREATE_ORDER,
                action="FORWARD",
                status="SUCCESS",
                details=f"Transação distribuída concluída. Pedido {order.order_id} CONFIRMED.",
            )
        )

        return SagaResult(
            saga_id=saga_id,
            order_id=order.order_id,
            final_status=SagaStatus.SUCCESS,
            history=history,
        )

    def _compensate_delivery(self, dispatch_id: str, history: List[SagaExecutionLog]) -> None:
        self._delivery.cancel_delivery(dispatch_id)
        history.append(
            SagaExecutionLog(
                step=SagaStep.SCHEDULE_DELIVERY,
                action="COMPENSATION",
                status="SUCCESS",
                details=f"Coleta de entrega {dispatch_id} cancelada com sucesso.",
            )
        )

    def _compensate_inventory(self, reservation_id: str, history: List[SagaExecutionLog]) -> None:
        self._inventory.release_inventory(reservation_id)
        history.append(
            SagaExecutionLog(
                step=SagaStep.RESERVE_INVENTORY,
                action="COMPENSATION",
                status="SUCCESS",
                details=f"Reserva {reservation_id} liberada e estoque devolvido ao saldo.",
            )
        )

    def _compensate_payment(self, payment_id: str, history: List[SagaExecutionLog]) -> None:
        self._payment.refund_payment(payment_id)
        history.append(
            SagaExecutionLog(
                step=SagaStep.PROCESS_PAYMENT,
                action="COMPENSATION",
                status="SUCCESS",
                details=f"Pagamento {payment_id} estornado integralmente ao cliente.",
            )
        )

    def _compensate_order(
        self, order_id: str, reason: str, history: List[SagaExecutionLog]
    ) -> None:
        self._order.cancel_order(order_id, reason)
        history.append(
            SagaExecutionLog(
                step=SagaStep.CREATE_ORDER,
                action="COMPENSATION",
                status="SUCCESS",
                details=f"Pedido {order_id} cancelado no banco de pedidos devido a: {reason}.",
            )
        )
