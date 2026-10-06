"""
infrastructure/rental_controller.py - Camada 4: UI / Delivery Mechanism.
"""

from __future__ import annotations
from typing import Dict, Any, Tuple
from application.dto import OpenRentalCommand, CloseRentalCommand
from application.rental_service import RentalFleetApplicationService


class RentalFleetController:
    def __init__(self, rental_service: RentalFleetApplicationService) -> None:
        self.rental_service = rental_service

    def handle_post_open_rental(self, payload: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        cmd = OpenRentalCommand(
            customer_name=payload.get("customer", ""),
            vehicle_id=payload.get("vehicle_id", ""),
            rental_days=int(payload.get("days", 1)),
        )
        res = self.rental_service.open_rental(cmd)

        if res.success:
            return 201, {
                "status": "OPENED",
                "contract_id": res.contract_id,
                "customer": res.customer_name,
                "vehicle": res.vehicle_model,
                "days": res.days,
                "base_charged": f"R$ {res.base_charge:.2f}",
                "message": res.message,
            }
        else:
            return 400, {
                "status": "REJECTED",
                "message": res.message,
            }

    def handle_post_close_rental(self, payload: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        cmd = CloseRentalCommand(
            contract_id=payload.get("contract_id", ""),
            return_odometer_km=float(payload.get("return_odometer", 0.0)),
            return_fuel_eighths=int(payload.get("return_fuel_eighths", 8)),
            damages=payload.get("damages", []),
        )
        res = self.rental_service.close_rental(cmd)

        if res.success:
            return 200, {
                "status": "CLOSED",
                "contract_id": res.contract_id,
                "base_charge": f"R$ {res.base_charge:.2f}",
                "extra_fees": f"R$ {res.extra_fees:.2f}",
                "breakdown": res.fee_breakdown,
                "total_paid": f"R$ {res.total_charged:.2f}",
                "message": res.message,
            }
        else:
            return 400, {
                "status": "ERROR",
                "message": res.message,
            }
