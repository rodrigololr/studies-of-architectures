"""
currency_converter_filter.py - Filtro 4: Conversão Cambial.

Converte moedas estrangeiras (USD, EUR) para a moeda contábil oficial (BRL)
com base em uma tabela de cotações configurada.
"""

from __future__ import annotations
from typing import Dict, Optional
from pipeline.base import Filter
from pipeline.context import TransactionRecord


class CurrencyConverterFilter(Filter[TransactionRecord, TransactionRecord]):
    def __init__(self, exchange_rates: Dict[str, float]) -> None:
        # Cotação base: 1 USD = 5.40 BRL, 1 EUR = 5.85 BRL, BRL = 1.0
        self.exchange_rates = exchange_rates

    def process(self, record: TransactionRecord) -> Optional[TransactionRecord]:
        if not record.is_valid:
            return record

        curr = record.currency
        rate = self.exchange_rates.get(curr)

        if rate is None:
            record.is_valid = False
            record.error_message = f"Moeda '{curr}' não suportada para conversão cambial."
            return record

        converted = record.original_amount * rate
        record.amount_brl = round(converted, 2)
        return record
