"""
main.py - Camada 4: Infrastructure (Composition Root da Onion Architecture).
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from domain.model.employee import Employee
from infrastructure.repositories import InMemoryEmployeeRepository, InMemoryPayrollSlipRepository
from infrastructure.bank_gateway import MockBankPayrollTransferGateway
from infrastructure.hr_console_controller import HrPayrollConsoleController
from application.payroll_service import PayrollApplicationService


def main() -> None:
    print("=" * 80)
    print(" ONION ARCHITECTURE - EXEMPLO 02: PAYROLL PROCESSING & PROGRESSIVE TAXES")
    print("=" * 80)

    # 1. Configuração dos Colaboradores (Infraestrutura)
    employee_repo = InMemoryEmployeeRepository({
        "emp_01": Employee(
            employee_id="emp_01",
            name="Ana Clara Souza",
            cpf="111.222.333-44",
            job_title="Desenvolvedora Júnior",
            base_salary=3000.00,
            dependents_count=0,
            meal_voucher_opt_in=True,
        ),
        "emp_02": Employee(
            employee_id="emp_02",
            name="Bruno Meirelles",
            cpf="222.333.444-55",
            job_title="Tech Lead Sênior",
            base_salary=8500.00,
            dependents_count=2,  # 2 dependentes abatem no IRPF
            meal_voucher_opt_in=True,
        ),
        "emp_03": Employee(
            employee_id="emp_03",
            name="Camila Duarte",
            cpf="333.444.555-66",
            job_title="Diretora de Engenharia",
            base_salary=24000.00,
            dependents_count=1,
            meal_voucher_opt_in=False,
        ),
    })

    slip_repo = InMemoryPayrollSlipRepository()
    bank_gw = MockBankPayrollTransferGateway()

    # 2. Montagem do Application Service
    payroll_service = PayrollApplicationService(
        employee_repo=employee_repo,
        slip_repo=slip_repo,
        bank_gateway=bank_gw,
    )

    controller = HrPayrollConsoleController(payroll_service=payroll_service)

    print("\n--- CENÁRIO 1: Execução do Fechamento Mensal da Folha (Competência 2026-10) ---")
    status, res = controller.run_monthly_closure(reference_period="2026-10")
    print(f"Status HTTP: {status}")
    print(json.dumps(res, indent=2, ensure_ascii=False))

    print("\n--- CENÁRIO 2: Auditoria de Créditos Bancários Despachados ---")
    print(f"Total de transferências no lote bancário: {len(bank_gw.transfers_log)}")
    for emp_id, name, net in bank_gw.transfers_log:
        print(f" -> TED/PIX para {name:20} (ID: {emp_id}): R$ {net:,.2f}")

    print("\n--- CENÁRIO 3: Consulta Histórica de Contracheques no Repositório ---")
    history = slip_repo.list_by_period("2026-10")
    print(f"Total de holerites arquivados para 2026-10: {len(history)}")
    for h in history:
        print(f" -> [{h.payslip_id}] {h.employee_name:20} | Bruto: R$ {h.gross_salary:9.2f} | INSS: R$ {h.inss_deduction:6.2f} | IRPF: R$ {h.irpf_deduction:7.2f} | Líquido: R$ {h.net_salary:9.2f}")

    print("\n" + "=" * 80)
    print(" Exemplo 02 de Onion Architecture finalizado com sucesso!")
    print("=" * 80)


if __name__ == "__main__":
    main()
