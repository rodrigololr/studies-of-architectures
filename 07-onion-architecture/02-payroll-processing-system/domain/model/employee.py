"""
domain/model/employee.py - Camada 1: Domain Model.
"""

from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class Employee:
    employee_id: str
    name: str
    cpf: str
    job_title: str
    base_salary: float
    dependents_count: int = 0
    meal_voucher_opt_in: bool = True
    is_active: bool = True
