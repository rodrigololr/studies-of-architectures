"""Backend-for-Frontend (BFF) Web Desktop: Agregação rica e detalhada para navegadores."""

from typing import Dict, Any, Optional
from services.catalog_service import CatalogService
from services.pricing_service import PricingService
from services.inventory_service import InventoryService
from services.review_service import ReviewService


class WebDesktopBff:
    """BFF dedicado ao portal Web Desktop / E-commerce em telas grandes.
    
    Objetivo: Entregar página completa com galeria de alta resolução, especificações
    técnicas minuciosas, tabela de parcelamento e comentários recentes de clientes.
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

    def get_web_product_details(self, product_id: str) -> Optional[Dict[str, Any]]:
        # 1. Consulta ao Catálogo
        cat_data = self._catalog.get_product_by_id(product_id)
        if not cat_data:
            return None

        # 2. Consultas agregadas
        price_data = self._pricing.get_pricing_by_product_id(product_id) or {}
        inv_data = self._inventory.get_stock_by_product_id(product_id) or {}
        rev_data = self._review.get_reviews_by_product_id(product_id) or {}

        # 3. Formatação rica para Web
        return {
            "header": {
                "id": cat_data["id"],
                "title": cat_data["title"],
                "category_breadcrumb": cat_data["category"],
                "brand": cat_data["brand"],
            },
            "media_gallery": cat_data.get("images", []),
            "content": {
                "overview": cat_data["full_description"],
                "technical_specifications": cat_data.get("specs", {}),
            },
            "pricing_box": {
                "base_price": price_data.get("base_price", 0.0),
                "discount_percent": price_data.get("discount_percentage", 0.0),
                "cash_price": price_data.get("final_cash_price", 0.0),
                "installments_details": price_data.get("installments", {}),
                "currency": price_data.get("currency", "BRL"),
            },
            "logistics": {
                "in_stock": inv_data.get("in_stock", False),
                "available_units": inv_data.get("available_units", 0),
                "origin_warehouse": inv_data.get("warehouse_location", ""),
                "shipping_eta_days": inv_data.get("estimated_delivery_days", 0),
                "free_shipping": inv_data.get("free_shipping", False),
            },
            "customer_feedback": {
                "overall_score": rev_data.get("average_rating", 0.0),
                "total_ratings": rev_data.get("total_reviews", 0),
                "reviews_list": rev_data.get("recent_comments", []),
            },
        }
