"""
budget_view.py - Camada de Visão (View).

Formata as categorias do orçamento pessoal em relatórios com
barras de progresso textuais e indicadores de alerta de estouro.
"""

from __future__ import annotations
from typing import Dict, List
from models.budget_model import CategorySummary


class BudgetConsoleView:
    @staticmethod
    def render_report(summaries: List[CategorySummary], overall: Dict[str, float]) -> None:
        print("\n" + "=" * 80)
        print("💰 VISÃO ORÇAMENTÁRIA: RELATÓRIO MENSAL DE DESPESAS")
        print("=" * 80)
        header = f"{'CATEGORIA':<14} | {'TETO (R$)':<12} | {'GASTO (R$)':<12} | {'SALDO (R$)':<12} | {'USO (%)':<8} | STATUS"
        print(header)
        print("-" * 80)

        for s in summaries:
            lim_str = f"R$ {s.budget_limit:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            spt_str = f"R$ {s.total_spent:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            rem_str = f"R$ {s.remaining:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

            bar = BudgetConsoleView._draw_bar(s.spent_percentage)
            status_txt = "⚠️ ESTOURADO!" if s.is_over_budget else "✅ DENTRO"

            print(
                f"{s.category.value:<14} | {lim_str:<12} | {spt_str:<12} | {rem_str:<12} | {s.spent_percentage:>5.1f}%  | {bar} {status_txt}"
            )

        print("=" * 80)
        inc_str = f"R$ {overall['income']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        tot_str = f"R$ {overall['total_spent']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        sav_str = f"R$ {overall['net_savings']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        print(f"  • Renda Mensal Total:      {inc_str}")
        print(f"  • Despesas Realizadas:     {tot_str}")
        print(f"  • Saldo Poupança Líquido:  {sav_str}")
        print("=" * 80)

    @staticmethod
    def _draw_bar(percentage: float, width: int = 10) -> str:
        filled = min(width, int(round((percentage / 100.0) * width)))
        empty = width - filled
        return f"[{'█' * filled}{'░' * empty}]"
