"""
application/dto.py - Camada 3: Application DTOs.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class ProcessPayrollBatchCommand:
    reference_period: str  # ex: "2026-10"


@dataclass(frozen=True)
class PayslipSummaryDto:
    payslip_id: str
    employee_name: str
    job_title: str
    gross_salary: float
    inss: float
    irpf: float
    benefits: float
    net_salary: float


@dataclass(frozen=True)
class PayrollBatchResultDto:
    success: bool
    reference_period: str
    total_employees_processed: int
    total_gross_disbursed: float
    total_inss_collected: float
    total_irpf_withheld: float
    total_net_transferred: float
    slips: List[PayslipSummaryDto]
    message: str
