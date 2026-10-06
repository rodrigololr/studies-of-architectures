"""Ponto de Entrada e Facade do Módulo Orders."""

import uuid
from typing import Optional, List
from shared.events import InProcessEventBus
from modules.catalog.public_contracts import ICatalogModule
from modules.inventory.public_contracts import IInventoryModule, ReserveStockItem
from modules.payments.public_contracts import IPaymentsModule, ProcessPaymentCommand
from modules.orders.public_contracts import (
    IOrdersModule,
    PlaceOrderCommand,
    OrderSummaryDto,
    OrderPlacedDomainEvent,
    OrderCancelledDomainEvent,
)
from modules.orders.internal.orders_internal import (
    _InternalOrder,
    _InternalOrderItem,
    _InternalOrderRepository,
)


class OrdersModule(IOrdersModule):
    """Facade pública do módulo Orders.
    
    Orquestra o ciclo de vida do pedido interagindo unicamente com os
    contratos públicos dos outros módulos (Catalog, Inventory, Payments).
    """

    def __init__(
        self,
        catalog_module: ICatalogModule,
        inventory_module: IInventoryModule,
        payments_module: IPaymentsModule,
        event_bus: InProcessEventBus,
    ) -> None:
        self._catalog = catalog_module
        self._inventory = inventory_module
        self._payments = payments_module
        self._bus = event_bus
        self._repo = _InternalOrderRepository()

    def place_order(self, cmd: PlaceOrderCommand) -> OrderSummaryDto:
        order_id = f"ORD_{uuid.uuid4().hex[:8].upper()}"

        # 1. Consulta o Módulo de Catálogo para obter dados oficiais e precificação atualizada
        order_items: List[_InternalOrderItem] = []
        for item_in in cmd.items:
            product = self._catalog.get_by_sku(item_in.sku)
            if not product or not product.is_active:
                return OrderSummaryDto(
                    order_id=order_id,
                    customer_name=cmd.customer_name,
                    customer_email=cmd.customer_email,
                    status="FAILED_CATALOG",
                    total_amount=0.0,
                    items_count=0,
                    message=f"Produto SKU '{item_in.sku}' inexistente ou inativo no catálogo.",
                )
            order_items.append(_InternalOrderItem(
                sku=product.sku,
                product_name=product.name,
                unit_price=product.price,
                quantity=item_in.quantity,
            ))

        order = _InternalOrder(
            order_id=order_id,
            customer_name=cmd.customer_name,
            customer_email=cmd.customer_email,
            items=order_items,
            status="PENDING_STOCK",
        )

        # 2. Bloqueio Atômico no Módulo de Estoque
        stock_reservation = self._inventory.reserve_stock(
            order_id=order_id,
            items=[ReserveStockItem(sku=it.sku, quantity=it.quantity) for it in order_items],
        )

        if not stock_reservation.is_success:
            order.status = "STOCK_REJECTED"
            self._repo.save(order)
            return OrderSummaryDto(
                order_id=order.order_id,
                customer_name=order.customer_name,
                customer_email=order.customer_email,
                status=order.status,
                total_amount=order.total_amount,
                items_count=len(order.items),
                message=stock_reservation.message,
            )

        # 3. Dispara evento de pedido criado no barramento em memória
        order.status = "PENDING_PAYMENT"
        self._repo.save(order)
        self._bus.publish(OrderPlacedDomainEvent(
            order_id=order.order_id,
            customer_email=order.customer_email,
            total_amount=order.total_amount,
        ))

        # 4. Invocação síncrona do Módulo de Pagamentos
        payment_res = self._payments.process_payment(ProcessPaymentCommand(
            order_id=order.order_id,
            customer_email=order.customer_email,
            amount=order.total_amount,
            payment_method=cmd.payment_method,
        ))

        if payment_res.is_successful:
            order.status = "PAID"
            # Baixa definitiva de estoque
            self._inventory.commit_stock(order.order_id)
            self._repo.save(order)
            return OrderSummaryDto(
                order_id=order.order_id,
                customer_name=order.customer_name,
                customer_email=order.customer_email,
                status=order.status,
                total_amount=order.total_amount,
                items_count=len(order.items),
                message=f"Pedido faturado e pago com sucesso (Auth: {payment_res.auth_code}).",
            )
        else:
            order.status = "CANCELLED"
            # Compensação: Liberação do estoque reservado
            self._inventory.release_stock(order.order_id)
            self._bus.publish(OrderCancelledDomainEvent(
                order_id=order.order_id,
                reason=payment_res.error_message or "Pagamento recusado.",
            ))
            self._repo.save(order)
            return OrderSummaryDto(
                order_id=order.order_id,
                customer_name=order.customer_name,
                customer_email=order.customer_email,
                status=order.status,
                total_amount=order.total_amount,
                items_count=len(order.items),
                message=f"Pedido cancelado devido a falha no pagamento: {payment_res.error_message}",
            )

    def get_order(self, order_id: str) -> Optional[OrderSummaryDto]:
        order = self._repo.find_by_id(order_id)
        if not order:
            return None
        return OrderSummaryDto(
            order_id=order.order_id,
            customer_name=order.customer_name,
            customer_email=order.customer_email,
            status=order.status,
            total_amount=order.total_amount,
            items_count=len(order.items),
        )
