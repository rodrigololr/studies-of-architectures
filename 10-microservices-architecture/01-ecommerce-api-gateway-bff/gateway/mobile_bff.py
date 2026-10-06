"""Backend-for-Frontend (BFF) Mobile: Agregação e compressão de dados sob medida para Smartphones."""

from typing import Dict, Any, Optional
from services.catalog_service import CatalogService
from services.pricing_service import PricingService
from services.inventory_service import InventoryService
from services.review_service import ReviewService


class MobileBff:
    """BFF dedicado ao aplicativo móvel iOS / Android.
    
    Objetivo: Maximizar a velocidade de renderização e economizar pacote de dados 4G/5G,
    removendo campos desnecessários e agregando múltiplas chamadas em uma única resposta compacta.
    """

    def __init__(
        self,
        catalog: CatalogService,
        pricing: PricingService,
        inventory: InventoryService,
        review: ReviewService,
    ) -> None:
        self._catalog = catalog
        self._pricing = pricing
        self._inventory = inventory
        self._review = review

    def get_mobile_product_details(self, product_id: str) -> Optional[Dict[str, Any]]:
        # 1. Consulta ao microsserviço de catálogo
        cat_data = self._catalog.get_product_by_id(product_id)
        if not cat_data:
            return None

        # 2. Consultas concorrentes/agregadas aos outros microsserviços
        price_data = self._pricing.get_pricing_by_product_id(product_id) or {}
        inv_data = self._inventory.get_stock_by_product_id(product_id) or {}
        rev_data = self._review.get_reviews_by_product_id(product_id) or {}

        # 3. Formatação compacta (BFF Data Tailoring)
        installments = price_data.get("installments", {})
        inst_text = (
            f"{installments.get('max_installments')}x de R$ {installments.get('installment_value', 0):.2f} sem juros"
            if installments.get("interest_free")
            else "À vista"
        )

        return {
            "id": cat_data["id"],
            "title": cat_data["title"],
            "thumbnail_url": cat_data["images"][0] if cat_data.get("images") else "",
            "tagline": cat_data["short_description"],
            "price_formatted": f"R$ {price_data.get('final_cash_price', 0):,.2f}",
            "installment_summary": inst_text,
            "has_stock": inv_data.get("in_stock", False),
            "fast_delivery_days": inv_data.get("estimated_delivery_days", 0),
            "rating_score": rev_data.get("average_rating", 0.0),
            "reviews_count": rev_data.get("total_reviews", 0),
        }
