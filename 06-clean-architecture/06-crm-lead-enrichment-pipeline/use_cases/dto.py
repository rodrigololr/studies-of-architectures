"""
use_cases/dto.py - Camada 2: DTOs para Enriquecimento de Leads.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class IngestLeadRequestModel:
    name: str
    corporate_email: str
    company_name: str
    job_title: str


@dataclass(frozen=True)
class IngestLeadResponseModel:
    success: bool
    lead_id: Optional[str]
    company_name: Optional[str]
    score: int
    qualification: str
    assigned_sales_rep: Optional[str]
    employee_count: int
    annual_revenue: float
    message: str
