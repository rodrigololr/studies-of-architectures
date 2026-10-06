"""
base.py - Abstrações do Pipeline de Observabilidade e Segurança de Logs.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar

TIn = TypeVar("TIn")
TOut = TypeVar("TOut")


class Filter(ABC, Generic[TIn, TOut]):
    @abstractmethod
    def process(self, data: TIn) -> Optional[TOut]:
        pass


class LogPipeline:
    def __init__(self) -> None:
        self._filters: List[Filter] = []

    def add_filter(self, filter_instance: Filter) -> LogPipeline:
        self._filters.append(filter_instance)
        return self

    def execute(self, log_data: any) -> any:
        current = log_data
        for f in self._filters:
            current = f.process(current)
            if current is None:
                return None
        return current
