"""
shunting_yard_filter.py - Filtro 3: Parser e Conversor para Notação Pós-fixa (RPN).

Aplica o clássico algoritmo Shunting-Yard de Edsger Dijkstra para converter
a expressão infixa em notação polonesa reversa, respeitando precedências.
"""

from __future__ import annotations
from typing import Dict, List, Optional
from pipeline.base import Filter
from pipeline.context import CompilerContext, Token, TokenType


class ShuntingYardFilter(Filter[CompilerContext, CompilerContext]):
    PRECEDENCE: Dict[TokenType, int] = {
        TokenType.PLUS: 1,
        TokenType.MINUS: 1,
        TokenType.MULTIPLY: 2,
        TokenType.DIVIDE: 2,
    }

    def process(self, ctx: CompilerContext) -> Optional[CompilerContext]:
        if not ctx.is_valid:
            return ctx

        output_queue: List[Token] = []
        operator_stack: List[Token] = []

        for token in ctx.tokens:
            if token.token_type == TokenType.NUMBER:
                output_queue.append(token)

            elif token.token_type in self.PRECEDENCE:
                curr_prec = self.PRECEDENCE[token.token_type]
                while (
                    operator_stack
                    and operator_stack[-1].token_type in self.PRECEDENCE
                    and self.PRECEDENCE[operator_stack[-1].token_type] >= curr_prec
                ):
                    output_queue.append(operator_stack.pop())
                operator_stack.append(token)

            elif token.token_type == TokenType.LPAREN:
                operator_stack.append(token)

            elif token.token_type == TokenType.RPAREN:
                while operator_stack and operator_stack[-1].token_type != TokenType.LPAREN:
                    output_queue.append(operator_stack.pop())
                if operator_stack and operator_stack[-1].token_type == TokenType.LPAREN:
                    operator_stack.pop()

        while operator_stack:
            output_queue.append(operator_stack.pop())

        ctx.postfix_tokens = output_queue
        return ctx
