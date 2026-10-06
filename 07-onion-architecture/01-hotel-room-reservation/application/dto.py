"""
application/dto.py - Camada 3: Application DTOs.
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(frozen=True)
class CreateReservationCommand:
    guest_id: str
    guest_name: str
    guest_email: str
    guest_document: str
    room_number: str
    check_in_date: date
    check_out_date: date


@dataclass(frozen=True)
class ReservationResponseDto:
    success: bool
    reservation_id: Optional[str]
    guest_name: Optional[str]
    room_number: Optional[str]
    nights_count: int
    total_amount: float
    status: str
    message: str


@dataclass(frozen=True)
class CancelReservationCommand:
    reservation_id: str


@dataclass(frozen=True)
class CancelReservationResponseDto:
    success: bool
    reservation_id: str
    status: str
    cancellation_fee: float
    refund_amount: float
    message: str
