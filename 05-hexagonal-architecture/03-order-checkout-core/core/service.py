"""
service.py - Núcleo da Aplicação (Core / Hexágono) para Checkout de Pedidos.
"""

from __future__ import annotations
from typing import Optional
from domain.models import (
    CheckoutCommand,
    CheckoutResult,
    Order,
    OrderStatus,
)
from domain.exceptions import (
    EmptyCartException,
    InsufficientStockException,
    PaymentAuthorizationException,
)
from ports.driver import CheckoutUseCasePort, GetOrderStatusUseCasePort
from ports.driven import (
    InventoryReservationPort,
    ShippingCalculatorPort,
    PaymentGatewayPort,
    FiscalInvoicePort,
    OrderRepositoryPort,
)


class OrderCheckoutService(CheckoutUseCasePort, GetOrderStatusUseCasePort):
    def __init__(
        self,
        inventory_port: InventoryReservationPort,
        shipping_port: ShippingCalculatorPort,
        payment_port: PaymentGatewayPort,
        invoice_port: FiscalInvoicePort,
        order_repo: OrderRepositoryPort,
    ) -> None:
        self.inventory_port = inventory_port
        self.shipping_port = shipping_port
        self.payment_port = payment_port
        self.invoice_port = invoice_port
        self.order_repo = order_repo

    def execute_checkout(self, command: CheckoutCommand) -> CheckoutResult:
        # 1. Regra de Domínio: Carrinho não pode ser vazio
        if not command.items:
            raise EmptyCartException("Não é possível fechar um pedido sem itens.")

        # 2. Cálculo dos totais
        items_total = round(sum(item.subtotal for item in command.items), 2)
        shipping_fee = self.shipping_port.calculate_shipping(command.customer.postal_code, command.items)
        grand_total = round(items_total + shipping_fee, 2)

        # 3. Reserva de Estoque (Driven Port)
        stock_reserved = self.inventory_port.reserve_stock(command.order_id, command.items)
        if not stock_reserved:
            raise InsufficientStockException(f"Estoque insuficiente para os itens do pedido {command.order_id}.")

        # 4. Captura Financeira com Compensação (Driven Port)
        try:
            payment_confirmation = self.payment_port.charge(
                order_id=command.order_id,
                amount=grand_total,
                customer=command.customer,
                card_token=command.card_token,
            )
        except Exception as pay_err:
            # Compensação / Rollback de Estoque em caso de recusa financeira
            self.inventory_port.release_stock(command.order_id, command.items)
            failed_order = Order(
                order_id=command.order_id,
                customer=command.customer,
                items=command.items,
                items_total=items_total,
                shipping_fee=shipping_fee,
                grand_total=grand_total,
                status=OrderStatus.FAILED_PAYMENT,
            )
            self.order_repo.save(failed_order)
            raise PaymentAuthorizationException(f"Pagamento não autorizado: {str(pay_err)}")

        # 5. Criação do Pedido Aprovado
        order = Order(
            order_id=command.order_id,
            customer=command.customer,
            items=command.items,
            items_total=items_total,
            shipping_fee=shipping_fee,
            grand_total=grand_total,
            status=OrderStatus.APPROVED,
            payment_info=payment_confirmation,
        )

        # 6. Emissão de NF-e (Driven Port)
        invoice = self.invoice_port.issue_invoice(order)
        order.invoice_info = invoice

        # 7. Persistência Final (Driven Port)
        self.order_repo.save(order)

        return CheckoutResult(
            order_id=order.order_id,
            status=order.status,
            items_total=order.items_total,
            shipping_fee=order.shipping_fee,
            grand_total=order.grand_total,
            authorization_code=payment_confirmation.authorization_code,
            invoice_number=invoice.invoice_number,
        )

    def get_order(self, order_id: str) -> Optional[Order]:
        return self.order_repo.find_by_id(order_id)
