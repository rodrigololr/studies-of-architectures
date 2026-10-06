"""
interface_adapters/presenters.py - Camada 3: Presenter de Qualificação de Leads.
"""

from __future__ import annotations
from typing import Dict, Any
from use_cases.dto import IngestLeadResponseModel
from use_cases.boundaries import IngestLeadOutputBoundary


class LeadQualificationPresenter(IngestLeadOutputBoundary):
    def __init__(self) -> None:
        self.status_code: int = 200
        self.response_body: Dict[str, Any] = {}

    def present(self, response: IngestLeadResponseModel) -> None:
        if response.success:
            self.status_code = 201
            self.response_body = {
                "status": "QUALIFIED",
                "lead": {
                    "id": response.lead_id,
                    "company": response.company_name,
                    "score": response.score,
                    "tier": response.qualification,
                    "owner": response.assigned_sales_rep,
                },
                "enrichment": {
                    "employees": response.employee_count,
                    "revenue_usd": f"${response.annual_revenue:,.2f}",
                },
                "meta": {"message": response.message},
            }
        else:
            self.status_code = 400
            self.response_body = {
                "status": "DISQUALIFIED",
                "error": response.message,
            }
