"""
dashboard_view.py - Camada de Visão (View).

Responsável por formatar os dados do Model visualmente para o usuário:
- AsciiTableView: Tabela estruturada de oportunidades.
- KpiDashboardView: Painel executivo com cards e gráficos de barras textuais.
"""

from __future__ import annotations
from typing import Dict, List
from models.crm_model import Lead, LeadStage


class AsciiTableView:
    @staticmethod
    def render(leads: List[Lead]) -> None:
        print("\n" + "=" * 76)
        print("📋 VISÃO OPERACIONAL: TABELA DE LEADS NO PIPELINE")
        print("=" * 76)
        header = f"{'ID':<10} | {'CONTATO':<18} | {'EMPRESA':<18} | {'VALOR (R$)':<12} | {'ESTÁGIO'}"
        print(header)
        print("-" * 76)
        for lead in leads:
            val_str = f"R$ {lead.estimated_value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            print(
                f"{lead.lead_id:<10} | {lead.contact_name:<18} | {lead.company_name:<18} | {val_str:<12} | {lead.stage.value}"
            )
        print("=" * 76)


class KpiDashboardView:
    @staticmethod
    def render(metrics: Dict[str, float], leads: List[Lead]) -> None:
        print("\n" + "=" * 76)
        print("📊 VISÃO EXECUTIVA: DASHBOARD DE ANALYTICS DO CRM")
        print("=" * 76)
        rev_str = f"R$ {metrics['won_revenue']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        pipe_str = f"R$ {metrics['pipeline_total_value']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        ticket_str = f"R$ {metrics['average_ticket']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        print(f"  • Total de Oportunidades: {int(metrics['total_leads'])}")
        print(f"  • Oportunidades Ganhas:   {int(metrics['won_deals'])} ({metrics['conversion_rate_pct']}%)")
        print(f"  • Receita Fechada:        {rev_str}")
        print(f"  • Valor em Pipeline Ativo:{pipe_str}")
        print(f"  • Ticket Médio (Fechados):{ticket_str}")

        print("\n--- Distribuição Visual do Funil de Vendas ---")
        for stage in LeadStage:
            count = sum(1 for l in leads if l.stage == stage)
            bar = "█" * (count * 4) if count > 0 else " "
            print(f"  {stage.value:<12} | {bar:<24} ({count})")
        print("=" * 76)
