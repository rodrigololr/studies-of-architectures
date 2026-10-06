"""Pricing Microservice - Responsável exclusivo por tabelas de preços e promoções."""

from typing import Dict, Any, Optional


class PricingService:
    """Microsserviço de Preços com banco próprio (Database-per-Service)."""

    def __init__(self) -> None:
        self._db: Dict[str, Dict[str, Any]] = {
            "PROD-001": {
                "product_id": "PROD-001",
                "base_price": 7999.00,
                "discount_percentage": 15.0,
                "final_cash_price": 6799.15,
                "installments": {
                    "max_installments": 12,
                    "installment_value": 666.58,
                    "interest_free": True,
                },
                "currency": "BRL",
            },
            "PROD-002": {
                "product_id": "PROD-002",
                "base_price": 14999.00,
                "discount_percentage": 10.0,
                "final_cash_price": 13499.10,
                "installments": {
                    "max_installments": 10,
                    "installment_value": 1499.90,
                    "interest_free": True,
                },
                "currency": "BRL",
            },
        }

    def get_pricing_by_product_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        return self._db.get(product_id)
