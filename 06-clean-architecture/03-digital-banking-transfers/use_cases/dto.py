"""
use_cases/dto.py - Camada 2: DTOs para Transferências Bancárias.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class TransferFundsRequestModel:
    from_account: str
    destination_target: str  # Pode ser número de conta ou chave PIX
    amount: float
    method: str  # "PIX" | "TED"
    is_night_time: bool = False


@dataclass(frozen=True)
class TransferFundsResponseModel:
    success: bool
    transfer_id: Optional[str]
    from_account: Optional[str]
    to_account: Optional[str]
    amount: float
    remaining_balance: Optional[float]
    timestamp: Optional[str]
    message: str
