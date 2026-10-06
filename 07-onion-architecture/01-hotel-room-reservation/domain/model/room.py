"""
domain/model/room.py - Camada Central: Domain Model.
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


class RoomCategory(str, Enum):
    STANDARD = "STANDARD"
    DELUXE = "DELUXE"
    PRESIDENTIAL = "PRESIDENTIAL"


class RoomStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    OCCUPIED = "OCCUPIED"
    MAINTENANCE = "MAINTENANCE"


@dataclass
class Room:
    room_number: str
    category: RoomCategory
    base_daily_rate: float
    max_occupancy: int
    status: RoomStatus = RoomStatus.AVAILABLE

    def is_available(self) -> bool:
        return self.status == RoomStatus.AVAILABLE

    def mark_occupied(self) -> None:
        self.status = RoomStatus.OCCUPIED

    def mark_available(self) -> None:
        self.status = RoomStatus.AVAILABLE
