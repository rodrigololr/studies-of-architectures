"""
controller.py - Camada de Apresentação (Presentation Layer).

Recebe requisições de cadastro, entrada, reserva e expedição de produtos,
formatando a resposta e sinalizando alertas de reposição para a gestão de compras.
"""

from __future__ import annotations
from typing import Any, Dict
from business.service import InventoryService
from business.exceptions import (
    BusinessException,
    ProductNotFoundException,
    InsufficientStockException,
)


class InventoryController:
    def __init__(self, service: InventoryService) -> None:
        self.service = service

    def register_product(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """POST /api/inventory/products"""
        try:
            stock = self.service.register_product(
                sku=payload.get("sku", ""),
                product_name=payload.get("name", ""),
                initial_qty=int(payload.get("initial_qty", 0)),
                reorder_point=int(payload.get("reorder_point", 5)),
            )
            return {
                "status_code": 201,
                "data": {
                    "product_id": stock.product_id,
                    "sku": stock.sku,
                    "available": stock.available_qty,
                    "reorder_point": stock.reorder_point,
                },
            }
        except BusinessException as ex:
            return {"status_code": 400, "error": str(ex)}

    def reserve(self, product_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """POST /api/inventory/products/{id}/reserve"""
        try:
            qty = int(payload.get("quantity", 0))
            order_id = payload.get("order_id", "PED-0")
            stock = self.service.reserve_stock(product_id, qty, order_id)
            return {
                "status_code": 200,
                "data": {
                    "product_id": stock.product_id,
                    "available": stock.available_qty,
                    "reserved": stock.reserved_qty,
                    "total_physical": stock.total_physical_qty,
                },
            }
        except InsufficientStockException as ex:
            return {"status_code": 422, "error": str(ex)}
        except ProductNotFoundException as ex:
            return {"status_code": 404, "error": str(ex)}
        except BusinessException as ex:
            return {"status_code": 400, "error": str(ex)}

    def dispatch(self, product_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """POST /api/inventory/products/{id}/dispatch"""
        try:
            qty = int(payload.get("quantity", 0))
            order_id = payload.get("order_id", "PED-0")
            stock, alert = self.service.dispatch_reserved_stock(product_id, qty, order_id)
            return {
                "status_code": 200,
                "data": {
                    "product_id": stock.product_id,
                    "available": stock.available_qty,
                    "reserved": stock.reserved_qty,
                    "total_physical": stock.total_physical_qty,
                    "reorder_alert": alert,
                },
            }
        except InsufficientStockException as ex:
            return {"status_code": 422, "error": str(ex)}
        except ProductNotFoundException as ex:
            return {"status_code": 404, "error": str(ex)}
        except BusinessException as ex:
            return {"status_code": 400, "error": str(ex)}
