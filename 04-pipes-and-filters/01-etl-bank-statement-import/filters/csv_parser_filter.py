"""
csv_parser_filter.py - Filtro 1: Parser de Linhas CSV.

Recebe uma string bruta de linha CSV e decompõe em campos estruturados.
"""

from __future__ import annotations
from typing import Optional
from pipeline.base import Filter
from pipeline.context import TransactionRecord


class CsvRowParserFilter(Filter[str, TransactionRecord]):
    def process(self, raw_line: str) -> Optional[TransactionRecord]:
        line = raw_line.strip()
        if not line or line.startswith("#"):
            return None  # Descarta linhas em branco ou comentários

        parts = line.split(";")
        if len(parts) < 4:
            return TransactionRecord(
                raw_line=raw_line,
                is_valid=False,
                error_message=f"Linha CSV malformada: esperados 4 campos, obtidos {len(parts)}",
            )

        try:
            date_part, desc_part, amount_part, curr_part = parts[0], parts[1], parts[2], parts[3]
            amount = float(amount_part.replace(",", "."))
            return TransactionRecord(
                raw_line=raw_line,
                date_str=date_part.strip(),
                description=desc_part.strip(),
                original_amount=amount,
                currency=curr_part.strip().upper(),
                amount_brl=amount,
            )
        except ValueError as ex:
            return TransactionRecord(
                raw_line=raw_line, is_valid=False, error_message=f"Erro de conversão numérica: {ex}"
            )
