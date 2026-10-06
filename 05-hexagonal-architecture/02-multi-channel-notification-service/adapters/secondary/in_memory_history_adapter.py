"""
in_memory_history_adapter.py - Adaptador Secundário de Repositório de Histórico.
"""

from __future__ import annotations
from typing import List
from domain.models import DispatchResult
from ports.driven import NotificationHistoryRepositoryPort


class InMemoryNotificationHistoryAdapter(NotificationHistoryRepositoryPort):
    def __init__(self) -> None:
        self._history: List[DispatchResult] = []

    def record_dispatch(self, result: DispatchResult) -> None:
        self._history.append(result)

    def get_history(self) -> List[DispatchResult]:
        return list(self._history)
