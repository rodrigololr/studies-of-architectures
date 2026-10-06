"""
pii_masker_filter.py - Filtro 2: Mascaramento de Dados Pessoais Sensíveis (PII / LGPD).

Identifica e anonimiza CPFs, cartões de crédito e e-mails contidos no texto de mensagens de log.
"""

from __future__ import annotations
import re
from typing import Optional
from pipeline.base import Filter
from pipeline.context import LogEvent


class PiiMaskerFilter(Filter[LogEvent, LogEvent]):
    CPF_PATTERN = re.compile(r"\b(\d{3})\.(\d{3})\.(\d{3})-(\d{2})\b")
    CARD_PATTERN = re.compile(r"\b(\d{4})[ -]?(\d{4})[ -]?(\d{4})[ -]?(\d{4})\b")
    EMAIL_PATTERN = re.compile(r"\b([a-zA-Z0-9_.+-])[a-zA-Z0-9_.+-]*@([a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)\b")

    def process(self, event: LogEvent) -> Optional[LogEvent]:
        if not event.is_valid:
            return event

        text = event.message

        # 1. Mascara CPF: 123.456.789-00 -> ***.456.***-**
        text = self.CPF_PATTERN.sub(r"***.\2.***-**", text)

        # 2. Mascara Cartão: 4532 1234 5678 9012 -> 4532 **** **** 9012
        text = self.CARD_PATTERN.sub(r"\1 **** **** \4", text)

        # 3. Mascara E-mail: usuario@empresa.com -> u***@empresa.com
        text = self.EMAIL_PATTERN.sub(r"\1***@\2", text)

        event.message = text
        return event
