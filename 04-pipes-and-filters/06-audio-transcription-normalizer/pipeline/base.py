"""
base.py - Abstrações do Pipeline de Processamento de Áudio.
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


class AudioPipeline:
    def __init__(self) -> None:
        self._filters: List[Filter] = []

    def add_filter(self, filter_instance: Filter) -> AudioPipeline:
        self._filters.append(filter_instance)
        return self

    def execute(self, audio_data: any) -> any:
        current = audio_data
        for f in self._filters:
            current = f.process(current)
            if current is None or not getattr(current, "is_valid", True):
                return current
        return current
