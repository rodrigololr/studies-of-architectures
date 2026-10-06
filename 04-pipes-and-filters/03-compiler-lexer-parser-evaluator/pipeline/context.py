"""
context.py - Tokens e Contexto da Expressão através das fases do compilador.
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class TokenType(str, Enum):
    NUMBER = "NUMBER"
    PLUS = "+"
    MINUS = "-"
    MULTIPLY = "*"
    DIVIDE = "/"
    LPAREN = "("
    RPAREN = ")"


@dataclass(frozen=True)
class Token:
    token_type: TokenType
    value: str


@dataclass
class CompilerContext:
    raw_expression: str
    tokens: List[Token]
    postfix_tokens: List[Token]
    final_result: Optional[float] = None
    is_valid: bool = True
    error_message: Optional[str] = None
