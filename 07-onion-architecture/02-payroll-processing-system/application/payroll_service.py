"""
application/payroll_service.py - Camada 3: Application Service.
"""

from __future__ import annotations
import uuid
from datetime import datetime, timezone
from domain.model.payslip import Payslip
from domain.services.tax_calculator import BrazilianLaborTaxCalculatorService
from application.interfaces import (
    IEmployeeRepository,
    IPayrollSlipRepository,
    IBankPayrollTransferGateway,
)
from application.dto import (
    ProcessPayrollBatchCommand,
    PayrollBatchResultDto,
    PayslipSummaryDto,
)


class PayrollApplicationService:
    def __init__(
        self,
        employee_repo: IEmployeeRepository,
        slip_repo: IPayrollSlipRepository,
        bank_gateway: IBankPayrollTransferGateway,
    ) -> None:
        self.employee_repo = employee_repo
        self.slip_repo = slip_repo
        self.bank_gateway = bank_gateway

    def process_monthly_payroll(self, command: ProcessPayrollBatchCommand) -> PayrollBatchResultDto:
        # 1. Recupera funcionários ativos via repositório
        employees = self.employee_repo.list_active_employees()
        if not employees:
            return PayrollBatchResultDto(
                success=False,
                reference_period=command.reference_period,
                total_employees_processed=0,
                total_gross_disbursed=0.0,
                total_inss_collected=0.0,
                total_irpf_withheld=0.0,
                total_net_transferred=0.0,
                slips=[],
                message="Nenhum colaborador ativo encontrado para processamento da folha.",
            )

        slips_summary = []
        bank_transfers = []
        total_gross = 0.0
        total_inss = 0.0
        total_irpf = 0.0
        total_net = 0.0

        now = datetime.now(timezone.utc)

        # 2. Orquestra cada colaborador invocando o Domain Service
        for emp in employees:
            gross = emp.base_salary
            inss = BrazilianLaborTaxCalculatorService.calculate_inss(gross)
            irpf = BrazilianLaborTaxCalculatorService.calculate_irpf(gross, inss, emp.dependents_count)
            benefits = BrazilianLaborTaxCalculatorService.calculate_benefits(emp)
            net = round(gross - inss - irpf - benefits, 2)

            slip_id = f"PAY_{uuid.uuid4().hex[:8].upper()}"
            payslip = Payslip(
                payslip_id=slip_id,
                employee_id=emp.employee_id,
                employee_name=emp.name,
                reference_period=command.reference_period,
                gross_salary=gross,
                inss_deduction=inss,
                irpf_deduction=irpf,
                benefits_deduction=benefits,
                net_salary=net,
                generated_at=now,
            )

            # Persiste
            self.slip_repo.save(payslip)

            total_gross += gross
            total_inss += inss
            total_irpf += irpf
            total_net += net

            bank_transfers.append((emp.employee_id, emp.name, net))
            slips_summary.append(PayslipSummaryDto(
                payslip_id=slip_id,
                employee_name=emp.name,
                job_title=emp.job_title,
                gross_salary=gross,
                inss=inss,
                irpf=irpf,
                benefits=benefits,
                net_salary=net,
            ))

        # 3. Transmite remessa de pagamentos ao banco
        self.bank_gateway.dispatch_direct_deposits(bank_transfers)

        return PayrollBatchResultDto(
            success=True,
            reference_period=command.reference_period,
            total_employees_processed=len(employees),
            total_gross_disbursed=round(total_gross, 2),
            total_inss_collected=round(total_inss, 2),
            total_irpf_withheld=round(total_irpf, 2),
            total_net_transferred=round(total_net, 2),
            slips=slips_summary,
            message="Folha de pagamento processada e creditada com sucesso!",
        )
