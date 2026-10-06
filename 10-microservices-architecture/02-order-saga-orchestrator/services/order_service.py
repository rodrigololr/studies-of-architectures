"""Order Microservice - Gestor do ciclo de vida do pedido de compra."""

from typing import Dict, Any, Optional
from saga.saga_models import OrderStatus


class OrderService:
    """Microsserviço de Pedidos com banco próprio (Database-per-Service)."""

    def __init__(self) -> None:
        self._orders_db: Dict[str, Dict[str, Any]] = {}

    def create_pending_order(self, order_id: str, customer_id: str, total_amount: float) -> bool:
        self._orders_db[order_id] = {
            "order_id": order_id,
            "customer_id": customer_id,
            "total_amount": total_amount,
            "status": OrderStatus.PENDING,
            "cancellation_reason": None,
        }
        return True

    def confirm_order(self, order_id: str) -> bool:
        if order_id in self._orders_db:
            self._orders_db[order_id]["status"] = OrderStatus.CONFIRMED
            return True
        return False

    def cancel_order(self, order_id: str, reason: str) -> bool:
        """Ação Compensatória da Saga."""
        if order_id in self._orders_db:
            self._orders_db[order_id]["status"] = OrderStatus.CANCELLED
            self._orders_db[order_id]["cancellation_reason"] = reason
            return True
        return False

    def get_order_status(self, order_id: str) -> Optional[OrderStatus]:
        order = self._orders_db.get(order_id)
        return order["status"] if order else None
