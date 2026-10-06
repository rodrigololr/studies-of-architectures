"""
interface_adapters/presenters.py - Camada 3: Presenter de Despacho de Pedidos.
"""

from __future__ import annotations
from typing import Dict, Any
from use_cases.dto import MatchCourierResponseModel
from use_cases.boundaries import MatchCourierOutputBoundary


class DispatchRestPresenter(MatchCourierOutputBoundary):
    def __init__(self) -> None:
        self.status_code: int = 200
        self.response_body: Dict[str, Any] = {}

    def present(self, response: MatchCourierResponseModel) -> None:
        if response.success:
            self.status_code = 200
            self.response_body = {
                "status": "MATCHED",
                "order_id": response.order_id,
                "courier": {
                    "name": response.assigned_courier_name,
                    "vehicle": response.courier_vehicle,
                    "distance_to_pickup_km": response.distance_to_restaurant_km,
                },
                "logistics": {
                    "total_trip_km": response.trip_distance_km,
                    "delivery_fee_customer": response.delivery_fee,
                    "courier_payout": response.courier_payout,
                },
                "message": response.message,
            }
        else:
            self.status_code = 404
            self.response_body = {
                "status": "UNMATCHED",
                "order_id": response.order_id,
                "message": response.message,
            }
