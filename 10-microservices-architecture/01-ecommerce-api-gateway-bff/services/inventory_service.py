"""Inventory Microservice - Responsável exclusivo por estoque e logística de fulfillment."""

from typing import Dict, Any, Optional


class InventoryService:
    """Microsserviço de Estoque com banco próprio (Database-per-Service)."""

    def __init__(self) -> None:
        self._db: Dict[str, Dict[str, Any]] = {
            "PROD-001": {
                "product_id": "PROD-001",
                "in_stock": True,
                "available_units": 42,
                "warehouse_location": "CD-SAO-PAULO-01",
                "estimated_delivery_days": 2,
                "free_shipping": True,
            },
            "PROD-002": {
                "product_id": "PROD-002",
                "in_stock": True,
                "available_units": 5,
                "warehouse_location": "CD-CURITIBA-03",
                "estimated_delivery_days": 4,
                "free_shipping": True,
            },
        }

    def get_stock_by_product_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        return self._db.get(product_id)
