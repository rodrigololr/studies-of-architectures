"""Inventory Microservice - Reserva e liberação de itens de estoque."""

import uuid
from typing import Dict, Any, List, Tuple
from saga.saga_models import OrderItem


class InventoryService:
    """Microsserviço de Estoque com banco próprio (Database-per-Service)."""

    def __init__(self) -> None:
        # Saldo físico de estoque por produto
        self._stock_db: Dict[str, int] = {
            "SKU-IPHONE-15": 10,
            "SKU-MACBOOK-AIR": 3,
            "SKU-PS5-PRO": 0,  # Sem estoque para testar falha
        }
        self._reservations_db: Dict[str, Dict[str, Any]] = {}

    def reserve_inventory(
        self, order_id: str, items: List[OrderItem]
    ) -> Tuple[bool, str]:
        """Etapa direta: reserva o estoque se todos os itens estiverem disponíveis."""
        # 1. Checa disponibilidade de todos
        for item in items:
            available = self._stock_db.get(item.product_id, 0)
            if available < item.quantity:
                return False, f"Estoque insuficiente para o produto {item.product_id} (Disponível: {available}, Solicitado: {item.quantity})"

        # 2. Bloqueia o estoque
        reservation_id = f"RESV-{uuid.uuid4().hex[:8].upper()}"
        reserved_items = []
        for item in items:
            self._stock_db[item.product_id] -= item.quantity
            reserved_items.append((item.product_id, item.quantity))

        self._reservations_db[reservation_id] = {
            "reservation_id": reservation_id,
            "order_id": order_id,
            "items": reserved_items,
            "status": "HOLD",
        }
        return True, reservation_id

    def release_inventory(self, reservation_id: str) -> bool:
        """Ação Compensatória da Saga: Devolve os itens ao estoque disponível."""
        if reservation_id in self._reservations_db:
            resv = self._reservations_db[reservation_id]
            if resv["status"] == "HOLD":
                for product_id, qty in resv["items"]:
                    self._stock_db[product_id] = self._stock_db.get(product_id, 0) + qty
                resv["status"] = "RELEASED"
                return True
        return False

    def get_stock_level(self, product_id: str) -> int:
        return self._stock_db.get(product_id, 0)
