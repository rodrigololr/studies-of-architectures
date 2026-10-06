"""
domain/model/payslip.py - Camada 1: Domain Model.
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class Payslip:
    payslip_id: str
    employee_id: str
    employee_name: str
    reference_period: str  # ex: "2026-10"
    gross_salary: float
    inss_deduction: float
    irpf_deduction: float
    benefits_deduction: float
    net_salary: float
    generated_at: datetime
