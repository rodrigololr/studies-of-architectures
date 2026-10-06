"""
entities/exceptions.py - Camada 1: Exceções de Domínio de Delivery.
"""

from __future__ import annotations


class DeliveryEntityException(Exception):
    pass


class InvalidLocationException(DeliveryEntityException):
    pass
