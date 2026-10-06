"""
interface_adapters/controllers.py - Camada 3: Controller de Despacho de Pedidos.
"""

from __future__ import annotations
from typing import Dict, Any
from use_cases.dto import MatchCourierRequestModel
from use_cases.boundaries import MatchCourierInputBoundary


class DeliveryDispatchController:
    def __init__(self, match_use_case: MatchCourierInputBoundary) -> None:
        self.match_use_case = match_use_case

    def handle_post_dispatch(self, payload: Dict[str, Any]) -> None:
        req = MatchCourierRequestModel(
            order_id=payload.get("order_id", ""),
            restaurant_id=payload.get("restaurant_id", ""),
            customer_latitude=float(payload.get("customer_lat", 0.0)),
            customer_longitude=float(payload.get("customer_lon", 0.0)),
            items_subtotal=float(payload.get("subtotal", 0.0)),
            max_search_radius_km=float(payload.get("max_radius_km", 5.0)),
        )
        self.match_use_case.execute(req)
