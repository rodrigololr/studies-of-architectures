"""
date_validator_filter.py - Filtro 3: Validação de Datas.

Garante que a data esteja no formato estrito YYYY-MM-DD e represente um dia válido do calendário.
"""

from __future__ import annotations
from datetime import datetime
from typing import Optional
from pipeline.base import Filter
from pipeline.context import TransactionRecord


class DateValidatorFilter(Filter[TransactionRecord, TransactionRecord]):
    def process(self, record: TransactionRecord) -> Optional[TransactionRecord]:
        if not record.is_valid:
            return record

        try:
            parsed_date = datetime.strptime(record.date_str, "%Y-%m-%d")
            record.date_str = parsed_date.strftime("%Y-%m-%d")
        except ValueError:
            record.is_valid = False
            record.error_message = f"Data inválida ou fora do padrão ISO: '{record.date_str}'"

        return record
