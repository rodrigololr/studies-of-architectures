"""
domain/model/guest.py - Camada Central: Domain Model.
"""

from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class Guest:
    guest_id: str
    name: str
    email: str
    document_cpf_or_passport: str
