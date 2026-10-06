"""
domain/model/exceptions.py - Camada 1: Exceções de Domínio de Locação.
"""

from __future__ import annotations


class RentalDomainException(Exception):
    pass


class VehicleNotAvailableException(RentalDomainException):
    pass


class ContractNotFoundException(RentalDomainException):
    pass
