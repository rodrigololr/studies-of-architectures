"""
crm_model.py - Camada de Modelo (Model).

Contém as estruturas de dados de Leads e regras de negócio de métricas comerciais:
- Funil de vendas (PROSPECT -> QUALIFIED -> PROPOSAL -> CLOSED_WON / CLOSED_LOST).
- Cálculos estatísticos de conversão e ticket médio.
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional
import uuid


class LeadStage(str, Enum):
    PROSPECT = "PROSPECT"
    QUALIFIED = "QUALIFIED"
    PROPOSAL = "PROPOSAL"
    CLOSED_WON = "CLOSED_WON"
    CLOSED_LOST = "CLOSED_LOST"


@dataclass
class Lead:
    lead_id: str
    contact_name: str
    company_name: str
    estimated_value: float
    stage: LeadStage = LeadStage.PROSPECT


class CrmModel:
    def __init__(self) -> None:
        self._leads: Dict[str, Lead] = {}

    def add_lead(self, contact_name: str, company_name: str, value: float) -> Lead:
        if value < 0:
            raise ValueError("O valor estimado da oportunidade não pode ser negativo.")

        lead = Lead(
            lead_id=str(uuid.uuid4())[:8],
            contact_name=contact_name.strip(),
            company_name=company_name.strip(),
            estimated_value=round(value, 2),
            stage=LeadStage.PROSPECT,
        )
        self._leads[lead.lead_id] = lead
        return lead

    def advance_stage(self, lead_id: str, new_stage: LeadStage) -> Lead:
        lead = self._leads.get(lead_id)
        if not lead:
            raise KeyError(f"Lead com ID '{lead_id}' não encontrado.")
        lead.stage = new_stage
        return lead

    def list_all_leads(self) -> List[Lead]:
        return list(self._leads.values())

    def calculate_metrics(self) -> Dict[str, float]:
        leads = list(self._leads.values())
        total_count = len(leads)
        won_leads = [l for l in leads if l.stage == LeadStage.CLOSED_WON]
        won_count = len(won_leads)
        total_revenue = sum(l.estimated_value for l in won_leads)
        pipeline_total = sum(l.estimated_value for l in leads if l.stage not in (LeadStage.CLOSED_LOST,))

        conversion_rate = (won_count / total_count * 100) if total_count > 0 else 0.0
        avg_ticket = (total_revenue / won_count) if won_count > 0 else 0.0

        return {
            "total_leads": total_count,
            "won_deals": won_count,
            "conversion_rate_pct": round(conversion_rate, 1),
            "won_revenue": round(total_revenue, 2),
            "pipeline_total_value": round(pipeline_total, 2),
            "average_ticket": round(avg_ticket, 2),
        }
