"""Ponto de Entrada e Facade do Módulo Catalog (Implementa o Contrato Público)."""

from typing import Optional, List
from modules.catalog.public_contracts import ICatalogModule, ProductDto
from modules.catalog.internal.catalog_internal import _InternalProduct, _InternalCatalogRepository


class CatalogModule(ICatalogModule):
    """Facade pública do módulo Catalog."""
    def __init__(self) -> None:
        self._repo = _InternalCatalogRepository()

    def seed_product(self, product_id: str, sku: str, name: str, cost: float, price: float) -> None:
        """Método de inicialização / seed de dados de catálogo."""
        self._repo.save(_InternalProduct(
            product_id=product_id,
            sku=sku,
            name=name,
            cost_price=cost,
            sale_price=price,
        ))

    def get_product(self, product_id: str) -> Optional[ProductDto]:
        prod = self._repo.find_by_id(product_id)
        if not prod:
            return None
        return ProductDto(
            product_id=prod.product_id,
            sku=prod.sku,
            name=prod.name,
            price=prod.sale_price,
            is_active=prod.is_active,
        )

    def get_by_sku(self, sku: str) -> Optional[ProductDto]:
        prod = self._repo.find_by_sku(sku)
        if not prod:
            return None
        return ProductDto(
            product_id=prod.product_id,
            sku=prod.sku,
            name=prod.name,
            price=prod.sale_price,
            is_active=prod.is_active,
        )

    def list_catalog(self) -> List[ProductDto]:
        return [
            ProductDto(
                product_id=p.product_id,
                sku=p.sku,
                name=p.name,
                price=p.sale_price,
                is_active=p.is_active,
            )
            for p in self._repo.list_all() if p.is_active
        ]
