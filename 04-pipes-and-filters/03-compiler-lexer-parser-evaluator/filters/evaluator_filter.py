"""
evaluator_filter.py - Filtro 4: Avaliador da Pilha Pós-Fixa (Evaluator).

Consome a fila de tokens em RPN e computa o resultado aritmético final em ponto flutuante.
"""

from __future__ import annotations
from typing import List, Optional
from pipeline.base import Filter
from pipeline.context import CompilerContext, TokenType


class RpnEvaluatorFilter(Filter[CompilerContext, CompilerContext]):
    def process(self, ctx: CompilerContext) -> Optional[CompilerContext]:
        if not ctx.is_valid:
            return ctx

        stack: List[float] = []

        try:
            for token in ctx.postfix_tokens:
                if token.token_type == TokenType.NUMBER:
                    stack.append(float(token.value))
                elif token.token_type in (TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY, TokenType.DIVIDE):
                    if len(stack) < 2:
                        ctx.is_valid = False
                        ctx.error_message = "Erro de Avaliação: operandos insuficientes na pilha."
                        return ctx

                    b = stack.pop()
                    a = stack.pop()

                    if token.token_type == TokenType.PLUS:
                        stack.append(a + b)
                    elif token.token_type == TokenType.MINUS:
                        stack.append(a - b)
                    elif token.token_type == TokenType.MULTIPLY:
                        stack.append(a * b)
                    elif token.token_type == TokenType.DIVIDE:
                        if b == 0.0:
                            ctx.is_valid = False
                            ctx.error_message = "Erro de Execução: divisão por zero detectada na expressão."
                            return ctx
                        stack.append(a / b)

            if len(stack) == 1:
                ctx.final_result = round(stack[0], 4)
            else:
                ctx.is_valid = False
                ctx.error_message = "Erro de Avaliação: expressão malformada (operandos restantes na pilha)."

        except Exception as ex:
            ctx.is_valid = False
            ctx.error_message = f"Erro inesperado no avaliador: {ex}"

        return ctx
