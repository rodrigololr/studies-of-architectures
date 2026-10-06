"""
sanitizer_filter.py - Filtro 2: Sanitização e Normalização de Texto.

Remove múltiplos espaços, caracteres invisíveis e padroniza maiúsculas na descrição.
"""

from __future__ import annotations
import re
from typing import Optional
from pipeline.base import Filter
from pipeline.context import TransactionRecord


class SanitizerFilter(Filter[TransactionRecord, TransactionRecord]):
    def process(self, record: TransactionRecord) -> Optional[TransactionRecord]:
        if not record.is_valid:
            return record

        # Remove espaços duplos e caracteres de controle
        clean_desc = re.sub(r"\s+", " ", record.description).strip().upper()
        # Remove caracteres indesejados mantendo letras, números e pontuação comum
        clean_desc = re.sub(r"[^\w\s\-\.\/]", "", clean_desc)

        record.description = clean_desc
        return record
