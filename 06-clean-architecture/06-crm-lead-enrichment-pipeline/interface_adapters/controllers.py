"""
interface_adapters/controllers.py - Camada 3: Controller de Ingestão de Leads.
"""

from __future__ import annotations
from typing import Dict, Any
from use_cases.dto import IngestLeadRequestModel
from use_cases.boundaries import IngestLeadInputBoundary


class LeadIngestionController:
    def __init__(self, ingest_use_case: IngestLeadInputBoundary) -> None:
        self.ingest_use_case = ingest_use_case

    def handle_post_lead(self, payload: Dict[str, Any]) -> None:
        req = IngestLeadRequestModel(
            name=payload.get("name", ""),
            corporate_email=payload.get("email", ""),
            company_name=payload.get("company", ""),
            job_title=payload.get("job_title", ""),
        )
        self.ingest_use_case.execute(req)
