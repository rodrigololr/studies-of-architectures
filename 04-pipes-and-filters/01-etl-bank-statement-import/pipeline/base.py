"""
base.py - Abstrações centrais da Arquitetura Pipes and Filters.

Define a interface abstrata Filter e o orquestrador Pipeline.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Generic, List, TypeVar, Optional

TInput = TypeVar("TInput")
TOutput = TypeVar("TOutput")


class Filter(ABC, Generic[TInput, TOutput]):
    """Interface abstrata base para qualquer estágio de transformação."""

    @abstractmethod
    def process(self, data: TInput) -> Optional[TOutput]:
        """
        Recebe um dado, aplica a transformação e retorna o resultado.
        Retornar None indica que o registro foi descartado/filtrado pelo estágio.
        """
        pass


class Pipeline:
    """
    Duto encadeador de filtros (Pipes).
    Transporta o dado de saída de cada filtro para a entrada do próximo.
    """

    def __init__(self) -> None:
        self._filters: List[Filter] = []

    def add_filter(self, filter_instance: Filter) -> Pipeline:
        """Permite plugar novos filtros de forma fluente (Builder Pattern)."""
        self._filters.append(filter_instance)
        return self

    def execute(self, initial_data: any) -> any:
        """Executa o pipeline sequencialmente para um item."""
        current_data = initial_data
        for f in self._filters:
            current_data = f.process(current_data)
            if current_data is None:
                # O registro foi interrompido/filtrado nesta etapa
                return None
        return current_data
