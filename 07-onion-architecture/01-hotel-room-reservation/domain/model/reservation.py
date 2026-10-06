"""
domain/model/reservation.py - Camada Central: Domain Model.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from enum import Enum
from typing import Optional
from domain.model.room import Room
from domain.model.guest import Guest


class ReservationStatus(str, Enum):
    CONFIRMED = "CONFIRMED"
    CHECKED_IN = "CHECKED_IN"
    CHECKED_OUT = "CHECKED_OUT"
    CANCELLED = "CANCELLED"


@dataclass(frozen=True)
class DateRange:
    check_in: date
    check_out: date

    def __post_init__(self) -> None:
        if self.check_out <= self.check_in:
            raise ValueError("Data de check-out deve ser posterior à data de check-in.")

    @property
    def total_nights(self) -> int:
        return (self.check_out - self.check_in).days

    def overlaps_with(self, other: DateRange) -> bool:
        return self.check_in < other.check_out and self.check_out > other.check_in


@dataclass
class Reservation:
    reservation_id: str
    guest: Guest
    room: Room
    period: DateRange
    total_amount: float
    status: ReservationStatus = ReservationStatus.CONFIRMED
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    cancellation_fee: float = 0.0
    refund_amount: float = 0.0

    def cancel(self, fee: float, refund: float) -> None:
        self.status = ReservationStatus.CANCELLED
        self.cancellation_fee = fee
        self.refund_amount = refund
        self.room.mark_available()
