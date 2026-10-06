"""
syntax_validator_filter.py - Filtro 2: Análise Sintática e Balanceamento.

Verifica se os parênteses estão devidamente balanceados e se não há operadores soltos.
"""

from __future__ import annotations
from typing import Optional
from pipeline.base import Filter
from pipeline.context import CompilerContext, TokenType


class SyntaxValidatorFilter(Filter[CompilerContext, CompilerContext]):
    def process(self, ctx: CompilerContext) -> Optional[CompilerContext]:
        if not ctx.is_valid:
            return ctx

        tokens = ctx.tokens
        if not tokens:
            ctx.is_valid = False
            ctx.error_message = "Erro Sintático: expressão vazia."
            return ctx

        # 1. Balanceamento de parênteses
        open_parens = 0
        for t in tokens:
            if t.token_type == TokenType.LPAREN:
                open_parens += 1
            elif t.token_type == TokenType.RPAREN:
                open_parens -= 1
                if open_parens < 0:
                    ctx.is_valid = False
                    ctx.error_message = "Erro Sintático: parêntese de fechamento ')' sem abertura correspondente."
                    return ctx

        if open_parens != 0:
            ctx.is_valid = False
            ctx.error_message = "Erro Sintático: parênteses não balanceados."
            return ctx

        # 2. O último token não pode ser operador binário
        if tokens[-1].token_type in (TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY, TokenType.DIVIDE):
            ctx.is_valid = False
            ctx.error_message = f"Erro Sintático: expressão não pode terminar com operador '{tokens[-1].value}'."
            return ctx

        return ctx
