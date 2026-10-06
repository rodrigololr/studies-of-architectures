"""
interface_adapters/controllers.py - Camada 3: Controllers de Transferência.
"""

from __future__ import annotations
from typing import Dict, Any
from use_cases.dto import TransferFundsRequestModel
from use_cases.boundaries import TransferFundsInputBoundary


class TransferWebController:
    def __init__(self, transfer_use_case: TransferFundsInputBoundary) -> None:
        self.transfer_use_case = transfer_use_case

    def handle_post_transfer(self, payload: Dict[str, Any]) -> None:
        req = TransferFundsRequestModel(
            from_account=payload.get("from_account", ""),
            destination_target=payload.get("destination", ""),
            amount=float(payload.get("amount", 0.0)),
            method=payload.get("method", "PIX"),
            is_night_time=bool(payload.get("is_night_time", False)),
        )
        self.transfer_use_case.execute(req)
