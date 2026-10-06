"""
context.py - Estruturas de dados transportadas através dos Pipes.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass
class TransactionRecord:
    raw_line: str
    date_str: str = ""
    description: str = ""
    original_amount: float = 0.0
    currency: str = "BRL"
    amount_brl: float = 0.0
    category: str = "GERAL"
    is_valid: bool = True
    error_message: Optional[str] = None
