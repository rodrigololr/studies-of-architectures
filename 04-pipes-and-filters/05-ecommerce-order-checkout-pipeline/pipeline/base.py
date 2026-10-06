"""
base.py - Abstrações do Pipeline de Checkout com Interrupção Precoce (Short-Circuiting).
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


class OrderValidationPipeline:
    def __init__(self) -> None:
        self._filters: List[Filter] = []

    def add_filter(self, filter_instance: Filter) -> OrderValidationPipeline:
        self._filters.append(filter_instance)
        return self

    def execute(self, order_context: any) -> any:
        current = order_context
        for f in self._filters:
            current = f.process(current)
            if current is None or not getattr(current, "is_approved", True):
                # Short-circuiting: se um filtro reprovar, interrompe a esteira imediatamente
                return current
        return current
