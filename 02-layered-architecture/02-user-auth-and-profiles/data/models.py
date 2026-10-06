"""
models.py - Camada de Dados (Data Layer).
Modelos de dados para persistência de contas de usuário e perfis de acesso.
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    OPERATOR = "OPERATOR"
    CUSTOMER = "CUSTOMER"


@dataclass
class UserModel:
    user_id: str
    full_name: str
    email: str
    password_hash: str
    salt: str
    role: UserRole = UserRole.CUSTOMER
    is_active: bool = True
