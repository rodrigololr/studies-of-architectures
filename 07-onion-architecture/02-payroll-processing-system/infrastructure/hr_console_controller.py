"""
infrastructure/hr_console_controller.py - Camada 4: UI / Delivery Mechanism.
"""

from __future__ import annotations
from typing import Dict, Any, Tuple
from application.dto import ProcessPayrollBatchCommand
from application.payroll_service import PayrollApplicationService


class HrPayrollConsoleController:
    def __init__(self, payroll_service: PayrollApplicationService) -> None:
        self.payroll_service = payroll_service

    def run_monthly_closure(self, reference_period: str) -> Tuple[int, Dict[str, Any]]:
        cmd = ProcessPayrollBatchCommand(reference_period=reference_period)
        res = self.payroll_service.process_monthly_payroll(cmd)

        if res.success:
            return 200, {
                "status": "PROCESSED",
                "period": res.reference_period,
                "employees_count": res.total_employees_processed,
                "summary": {
                    "total_gross": f"R$ {res.total_gross_disbursed:,.2f}",
                    "inss_collected": f"R$ {res.total_inss_collected:,.2f}",
                    "irpf_withheld": f"R$ {res.total_irpf_withheld:,.2f}",
                    "net_credited": f"R$ {res.total_net_transferred:,.2f}",
                },
                "slips": [
                    {
                        "slip_id": s.payslip_id,
                        "name": s.employee_name,
                        "role": s.job_title,
                        "gross": f"R$ {s.gross_salary:.2f}",
                        "inss": f"R$ {s.inss:.2f}",
                        "irpf": f"R$ {s.irpf:.2f}",
                        "benefits": f"R$ {s.benefits:.2f}",
                        "net": f"R$ {s.net_salary:.2f}",
                    }
                    for s in res.slips
                ],
                "message": res.message,
            }
        else:
            return 400, {
                "status": "FAILED",
                "message": res.message,
            }
