"""
infrastructure/repositories.py - Camada 4: Infrastructure (Casca Externa).

Implementações concretas dos contratos abstratos declarados na camada de aplicação.
"""

from __future__ import annotations
from typing import Dict, List, Optional
from domain.model.room import Room
from domain.model.reservation import Reservation, DateRange
from application.interfaces import IRoomRepository, IReservationRepository


class InMemoryRoomRepository(IRoomRepository):
    def __init__(self, initial_rooms: Optional[Dict[str, Room]] = None) -> None:
        self._rooms: Dict[str, Room] = dict(initial_rooms or {})

    def find_by_number(self, room_number: str) -> Optional[Room]:
        return self._rooms.get(room_number)

    def find_available_rooms(self, period: DateRange) -> List[Room]:
        return [r for r in self._rooms.values() if r.is_available()]

    def save(self, room: Room) -> None:
        self._rooms[room.room_number] = room


class InMemoryReservationRepository(IReservationRepository):
    def __init__(self) -> None:
        self._reservations: Dict[str, Reservation] = {}

    def save(self, reservation: Reservation) -> None:
        self._reservations[reservation.reservation_id] = reservation

    def find_by_id(self, reservation_id: str) -> Optional[Reservation]:
        return self._reservations.get(reservation_id)

    def find_by_room_and_period(self, room_number: str, period: DateRange) -> List[Reservation]:
        conflicts = []
        for r in self._reservations.values():
            if r.room.room_number == room_number and r.period.overlaps_with(period):
                conflicts.append(r)
        return conflicts
