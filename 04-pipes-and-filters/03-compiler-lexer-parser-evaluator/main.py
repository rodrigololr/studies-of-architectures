"""
main.py - Demonstração executável do Mini Compilador de Expressões (Pipes and Filters).

Monta as 4 fases do compilador (Lexer -> Syntax Validator -> Shunting-Yard -> RPN Evaluator)
e processa uma variedade de expressões matemáticas e casos de erro sintático.
"""

from pipeline.base import CompilerPipeline
from pipeline.context import CompilerContext
from filters.lexer_filter import LexerFilter
from filters.syntax_validator_filter import SyntaxValidatorFilter
from filters.shunting_yard_filter import ShuntingYardFilter
from filters.evaluator_filter import RpnEvaluatorFilter


def main() -> None:
    print("=" * 82)
    print("DEMONSTRAÇÃO: Pipes and Filters (Mini Compilador e Avaliador de Expressões)")
    print("=" * 82)

    # 1. Montagem do Pipeline do Compilador
    compiler = CompilerPipeline()
    compiler.add_filter(LexerFilter())
    compiler.add_filter(SyntaxValidatorFilter())
    compiler.add_filter(ShuntingYardFilter())
    compiler.add_filter(RpnEvaluatorFilter())

    # 2. Casos de teste de expressões matemáticas
    test_expressions = [
        "(10 + 20) * 3",             # Esperado: 90.0
        "100 - 4 * 5 + 10",          # Precedência: 100 - 20 + 10 = 90.0
        "2 + (3 * (4 + 1))",         # Parênteses aninhados: 2 + (3 * 5) = 17.0
        "10 / (5 - 5)",              # Divisão por zero (capturado no avaliador)
        "(5 + 5) *",                 # Erro de sintaxe (operador pendente no final)
        "(10 + 20",                  # Erro de sintaxe (parêntese não fechado)
    ]

    print("\n--- Processando Expressões pelo Pipeline de Compilação ---")

    for expr in test_expressions:
        ctx = CompilerContext(raw_expression=expr, tokens=[], postfix_tokens=[])
        result: CompilerContext = compiler.execute(ctx)

        print(f"\n[EXPRESSÃO]: '{expr}'")
        if result.is_valid:
            tokens_str = " ".join(f"[{t.value}]" for t in result.tokens)
            rpn_str = " ".join(t.value for t in result.postfix_tokens)
            print(f"  1. Tokens Léxicos:    {tokens_str}")
            print(f"  2. Notação RPN:       {rpn_str}")
            print(f"  ✅ Resultado Avaliado:{result.final_result}")
        else:
            print(f"  ❌ FALHA NO ESTÁGIO:  {result.error_message}")

    print("\n" + "=" * 82)


if __name__ == "__main__":
    main()
