"""
lexer_filter.py - Filtro 1: Análise Léxica (Tokenizer).

Varre a string caractere a caractere e agrupa em tokens atômicos (números e operadores).
"""

from __future__ import annotations
import re
from typing import List, Optional
from pipeline.base import Filter
from pipeline.context import CompilerContext, Token, TokenType


class LexerFilter(Filter[CompilerContext, CompilerContext]):
    def process(self, ctx: CompilerContext) -> Optional[CompilerContext]:
        if not ctx.is_valid:
            return ctx

        expr = ctx.raw_expression.strip()
        tokens: List[Token] = []
        i = 0
        length = len(expr)

        while i < length:
            char = expr[i]

            if char.isspace():
                i += 1
                continue

            if char.isdigit() or char == ".":
                num_buf = ""
                while i < length and (expr[i].isdigit() or expr[i] == "."):
                    num_buf += expr[i]
                    i += 1
                tokens.append(Token(TokenType.NUMBER, num_buf))
                continue

            if char in ("+", "-", "*", "/", "(", ")"):
                tokens.append(Token(TokenType(char), char))
                i += 1
                continue

            # Caractere desconhecido / não suportado
            ctx.is_valid = False
            ctx.error_message = f"Erro Léxico: caractere inesperado '{char}' na posição {i}"
            return ctx

        ctx.tokens = tokens
        return ctx
