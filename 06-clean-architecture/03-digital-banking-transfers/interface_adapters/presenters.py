"""
interface_adapters/presenters.py - Camada 3: Presenters Bancários.
"""

from __future__ import annotations
from typing import Dict, Any
from use_cases.dto import TransferFundsResponseModel
from use_cases.boundaries import TransferFundsOutputBoundary


class TransferRestPresenter(TransferFundsOutputBoundary):
    def __init__(self) -> None:
        self.status_code: int = 200
        self.response_body: Dict[str, Any] = {}

    def present(self, response: TransferFundsResponseModel) -> None:
        if response.success:
            self.status_code = 200
            self.response_body = {
                "status": "APPROVED",
                "transfer": {
                    "id": response.transfer_id,
                    "origin_account": response.from_account,
                    "destination_account": response.to_account,
                    "transferred_amount": response.amount,
                    "updated_balance": response.remaining_balance,
                    "completed_at": response.timestamp,
                },
                "receipt_message": response.message,
            }
        else:
            self.status_code = 422
            self.response_body = {
                "status": "REJECTED",
                "reason": response.message,
                "origin_account": response.from_account,
                "current_balance": response.remaining_balance,
            }
