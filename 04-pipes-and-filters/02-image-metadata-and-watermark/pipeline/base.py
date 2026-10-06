"""
base.py - Abstrações do Pipeline de Mídia.
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


class ImagePipeline:
    def __init__(self) -> None:
        self._filters: List[Filter] = []

    def add_filter(self, filter_instance: Filter) -> ImagePipeline:
        self._filters.append(filter_instance)
        return self

    def execute(self, image_data: any) -> any:
        current = image_data
        for f in self._filters:
            current = f.process(current)
            if current is None:
                return None
        return current
