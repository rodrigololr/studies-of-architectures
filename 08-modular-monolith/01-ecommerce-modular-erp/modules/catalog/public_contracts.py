"""Contrato Público do Módulo Catalog (Public API / Facade Contract).

Apenas os DTOs e a interface definidos neste arquivo podem ser consumidos
por outros módulos do Monólito. Nenhuma classe interna de catalog/internal/ deve vazar.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List


@dataclass(frozen=True)
class ProductDto:
    """DTO imutável representando um produto para consumo externo."""
    product_id: str
    sku: str
    name: str
    price: float
    is_active: bool


class ICatalogModule(ABC):
    """Interface pública exposta pelo Módulo de Catálogo."""
    @abstractmethod
    def get_product(self, product_id: str) -> Optional[ProductDto]:
        pass

    @abstractmethod
    def get_by_sku(self, sku: str) -> Optional[ProductDto]:
        pass

    @abstractmethod
    def list_catalog(self) -> List[ProductDto]:
        pass
