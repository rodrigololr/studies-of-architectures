"""
categorizer_filter.py - Filtro 5: Enriquecimento e Categorização Contábil.

Classifica o tipo do lançamento contábil (RECEITA, DESPESA_FIXA, DESPESA_VARIAVEL)
com base em regras de palavras-chave da descrição.
"""

from __future__ import annotations
from typing import Optional
from pipeline.base import Filter
from pipeline.context import TransactionRecord


class CategorizerFilter(Filter[TransactionRecord, TransactionRecord]):
    def process(self, record: TransactionRecord) -> Optional[TransactionRecord]:
        if not record.is_valid:
            return record

        desc = record.description
        if any(term in desc for term in ("SALARIO", "DEPOSITO", "PIX RECEBIDO", "CLIENTE")):
            record.category = "RECEITA"
        elif any(term in desc for term in ("ALUGUEL", "ENEL", "CONDOMINIO", "SABESP", "INTERNET")):
            record.category = "DESPESA_FIXA"
        elif any(term in desc for term in ("RESTAURANTE", "UBER", "IFOOD", "AMAZON")):
            record.category = "DESPESA_VARIAVEL"
        else:
            record.category = "OUTROS"

        return record
