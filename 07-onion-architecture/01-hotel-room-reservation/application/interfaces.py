"""
application/interfaces.py - Camada 3: Application Interfaces (Contratos do Anel de Aplicação).

Na Onion Architecture, os contratos abstratos de repositórios e serviços de I/O
são declarados nas camadas internas. A camada de infraestrutura apenas os implementa.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import date
from domain.model.room import Room
from domain.model.reservation import Reservation, DateRange


class IRoomRepository(ABC):
    @abstractmethod
    def find_by_number(self, room_number: str) -> Optional[Room]:
        pass

    @abstractmethod
    def find_available_rooms(self, period: DateRange) -> List[Room]:
        pass

    @abstractmethod
    def save(self, room: Room) -> None:
        pass


class IReservationRepository(ABC):
    @abstractmethod
    def save(self, reservation: Reservation) -> None:
        pass

    @abstractmethod
    def find_by_id(self, reservation_id: str) -> Optional[Reservation]:
        pass

    @abstractmethod
    def find_by_room_and_period(self, room_number: str, period: DateRange) -> List[Reservation]:
        pass


class IPaymentService(ABC):
    @abstractmethod
    def process_charge(self, guest_id: str, amount: float, description: str) -> bool:
        pass

    @abstractmethod
    def process_refund(self, guest_id: str, amount: float) -> bool:
        pass
