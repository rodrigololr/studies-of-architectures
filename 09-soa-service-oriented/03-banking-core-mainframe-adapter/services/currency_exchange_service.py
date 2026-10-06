"""Serviço Corporativo de Câmbio (Foreign Exchange Service - FX)."""

from typing import Dict


class ForeignExchangeService:
    def __init__(self) -> None:
        # Cotação base para conversão em BRL
        self._rates: Dict[str, float] = {
            "USD": 5.40,
            "EUR": 5.85,
            "BRL": 1.00,
        }

    def convert_to_brl(self, amount: float, currency: str) -> float:
        rate = self._rates.get(currency.upper(), 1.0)
        return round(amount * rate, 2)
