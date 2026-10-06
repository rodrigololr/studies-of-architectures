"""
repository.py - Camada de Dados (Data Layer).
Acesso ao repositório de persistência de usuários com busca por email e id.
"""

from __future__ import annotations
from typing import Dict, Optional
from data.models import UserModel


class UserRepository:
    def __init__(self) -> None:
        self._table: Dict[str, UserModel] = {}

    def save(self, user: UserModel) -> UserModel:
        self._table[user.user_id] = user
        return user

    def find_by_id(self, user_id: str) -> Optional[UserModel]:
        return self._table.get(user_id)

    def find_by_email(self, email: str) -> Optional[UserModel]:
        normalized = email.strip().lower()
        for u in self._table.values():
            if u.email.strip().lower() == normalized:
                return u
        return None
