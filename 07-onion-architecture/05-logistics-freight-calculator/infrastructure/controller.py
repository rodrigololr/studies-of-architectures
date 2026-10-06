"""Controlador da camada externa (Ring 4 - Infrastructure)."""

from typing import Dict, Any
from application.freight_service import FreightApplicationService
from application.dtos import (
    CalculateFreightQuoteCommand,
    ConfirmFreightOrderCommand,
)
from domain.model.exceptions import FreightDomainException


class FreightCalculatorController:
    """Controlador que adapta chamadas externas para comandos de frete."""
    def __init__(self, freight_service: FreightApplicationService) -> None:
        self._freight_service = freight_service

    def post_quote(self, cmd: CalculateFreightQuoteCommand) -> Dict[str, Any]:
        try:
            res = self._freight_service.calculate_and_create_quote(cmd)
            return {
                "http_status": 200,
                "data": {
                    "quote_id": res.quote_id,
                    "truck_type": res.truck_type,
                    "physical_weight_kg": f"{res.physical_weight_kg:,.1f} kg",
                    "volume_m3": f"{res.volume_m3:,.2f} m³",
                    "taxable_weight_kg": f"{res.taxable_weight_kg:,.1f} kg",
                    "distance_km": f"{res.distance_km:,.1f} km",
                    "breakdown": {k: f"R$ {v:,.2f}" for k, v in res.breakdown.items()},
                    "total_freight_cost": f"R$ {res.total_freight_cost:,.2f}",
                }
            }
        except FreightDomainException as e:
            return {
                "http_status": 400,
                "data": {"status": "REJECTED", "error": str(e)}
            }

    def post_confirm_order(self, cmd: ConfirmFreightOrderCommand) -> Dict[str, Any]:
        try:
            res = self._freight_service.confirm_order(cmd)
            return {
                "http_status": 200,
                "data": {
                    "order_id": res.order_id,
                    "status": res.status,
                    "shipper_name": res.shipper_name,
                    "route": f"{res.origin_city} -> {res.destination_city}",
                    "total_cost": f"R$ {res.total_cost:,.2f}",
                    "message": res.message,
                }
            }
        except FreightDomainException as e:
            return {
                "http_status": 400,
                "data": {"status": "ERROR", "error": str(e)}
            }
