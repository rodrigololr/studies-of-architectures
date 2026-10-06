"""
crm_controller.py - Camada de Controlador (Controller).

Intermediário entre as ações do usuário, a lógica de negócio do Model
e a renderização das Views.
"""

from __future__ import annotations
from models.crm_model import CrmModel, LeadStage
from views.dashboard_view import AsciiTableView, KpiDashboardView


class CrmController:
    def __init__(self, model: CrmModel) -> None:
        self.model = model
        self.table_view = AsciiTableView()
        self.kpi_view = KpiDashboardView()

    def handle_create_lead(self, contact: str, company: str, value: float) -> str:
        lead = self.model.add_lead(contact, company, value)
        return lead.lead_id

    def handle_advance_lead(self, lead_id: str, new_stage: LeadStage) -> None:
        self.model.advance_stage(lead_id, new_stage)

    def display_operational_table(self) -> None:
        leads = self.model.list_all_leads()
        self.table_view.render(leads)

    def display_executive_kpis(self) -> None:
        metrics = self.model.calculate_metrics()
        leads = self.model.list_all_leads()
        self.kpi_view.render(metrics, leads)
