"""Implementação Interna Privada do Módulo Catalog.

Estas classes são internas ao módulo e NÃO devem ser importadas diretamente
por Orders, Payments ou Inventory.
"""

from dataclasses import dataclass
from typing import Dict, Optional, List


@dataclass
class _InternalProduct:
    """Entidade privada de catálogo."""
    product_id: str
    sku: str
    name: str
    cost_price: float
    sale_price: float
    is_active: bool = True


class _InternalCatalogRepository:
    """Repositório privado com persistência em memória do schema 'catalog'."""
    def __init__(self) -> None:
        self._db: Dict[str, _InternalProduct] = {}

    def save(self, product: _InternalProduct) -> None:
        self._db[product.product_id] = product

    def find_by_id(self, product_id: str) -> Optional[_InternalProduct]:
        return self._db.get(product_id)

    def find_by_sku(self, sku: str) -> Optional[_InternalProduct]:
        for prod in self._db.values():
            if prod.sku == sku:
                return prod
        return None

    def list_all(self) -> List[_InternalProduct]:
        return list(self._db.values())
