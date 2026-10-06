"""
domain/model/exceptions.py - Camada Central: Exceções de Domínio.
"""

from __future__ import annotations


class HotelDomainException(Exception):
    pass


class RoomUnavailableException(HotelDomainException):
    pass


class InvalidReservationPeriodException(HotelDomainException):
    pass


class ReservationNotFoundException(HotelDomainException):
    pass
