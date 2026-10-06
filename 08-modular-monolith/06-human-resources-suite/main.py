"""Ponto de Entrada e Demonstração Executável - Exemplo 06: Human Resources Suite.

Demonstra:
1. Módulos com Bounded Contexts em monólito: Employees, TimeTracking, Payroll, Performance.
2. Integração reativa via In-Process Event Bus:
   - Fechamento de ponto no TimeTracking comanda cálculo automático de holerite com horas extras e faltas no Payroll.
3. Avaliação de desempenho 360° isolada e segura.
"""

import sys
import json
from pathlib import Path

# Adiciona o diretório do exemplo ao sys.path
sys.path.insert(0, str(Path(__file__).parent))

from shared.events import InProcessEventBus
from modules.employees import EmployeesModule, RegisterEmployeeCommand
from modules.timetracking import TimeTrackingModule, CloseTimesheetCommand
from modules.payroll import PayrollModule
from modules.performance import PerformanceModule, SubmitReviewCommand


def main() -> None:
    print("=" * 80)
    print(" MODULAR MONOLITH - EXEMPLO 06: HUMAN RESOURCES & TALENT SUITE")
    print("=" * 80)

    # 1. Composição de Módulos e Barramento Intra-Processo
    event_bus = InProcessEventBus()

    employees = EmployeesModule()
    timetracking = TimeTrackingModule(event_bus=event_bus)
    payroll = PayrollModule(
        employees_module=employees,
        event_bus=event_bus,
    )
    performance = PerformanceModule()

    # --------------------------------------------------------------------------
    # CENÁRIO 1: Admissão e Cadastro de Colaboradores (Módulo Employees)
    # --------------------------------------------------------------------------
    print("\n--- CENÁRIO 1: Admissão de Colaboradores (Módulo Employees) ---")
    emp_1 = employees.register_employee(RegisterEmployeeCommand(
        name="Guilherme Boulos",
        cpf="111.222.333-44",
        role="Engenheiro de Software Sênior",
        department="Engenharia de Plataforma",
        base_salary=11_000.0,
    ))
    emp_2 = employees.register_employee(RegisterEmployeeCommand(
        name="Tabata Amaral",
        cpf="555.666.777-88",
        role="Tech Lead",
        department="Produtos Digitais",
        base_salary=15_000.0,
    ))
    print(f"Colaborador 1: {emp_1.name} | Cargo: {emp_1.role} | Salário Base: R$ {emp_1.base_salary:,.2f}")
    print(f"Colaborador 2: {emp_2.name} | Cargo: {emp_2.role} | Salário Base: R$ {emp_2.base_salary:,.2f}")

    # --------------------------------------------------------------------------
    # CENÁRIO 2: Fechamento de Ponto Eletrônico (Módulo TimeTracking)
    # --------------------------------------------------------------------------
    print("\n--- CENÁRIO 2: Fechamento Mensal de Espelho de Ponto (Maio/2026) ---")
    # Guilherme trabalhou 12h extras no mês
    sheet_1 = timetracking.close_month_timesheet(CloseTimesheetCommand(
        employee_id=emp_1.employee_id,
        month="2026-05",
        regular_hours_worked=160.0,
        overtime_hours=12.0,
        unexcused_absences_days=0,
    ))
    print(f"Ponto Guilherme fechado: {sheet_1.regular_hours}h regulares | {sheet_1.overtime_hours}h extras | {sheet_1.absences_days} faltas")

    # Tabata teve 2 dias de faltas injustificadas
    sheet_2 = timetracking.close_month_timesheet(CloseTimesheetCommand(
        employee_id=emp_2.employee_id,
        month="2026-05",
        regular_hours_worked=144.0,
        overtime_hours=0.0,
        unexcused_absences_days=2,
    ))
    print(f"Ponto Tabata fechado: {sheet_2.regular_hours}h regulares | {sheet_2.overtime_hours}h extras | {sheet_2.absences_days} faltas")

    # --------------------------------------------------------------------------
    # CENÁRIO 3: Holerite Calculado Reativamente pelo Módulo Payroll
    # --------------------------------------------------------------------------
    print("\n--- CENÁRIO 3: Holerites Processados Reativamente (Módulo Payroll) ---")
    payslip_1 = payroll.get_payslip(emp_1.employee_id, "2026-05")
    if payslip_1:
        print(f"Holerite de {emp_1.name} (Mês: {payslip_1.month}):")
        print(f" -> Salário Base: R$ {payslip_1.base_salary:,.2f}")
        print(f" -> Horas Extras (+50%): R$ {payslip_1.overtime_pay:,.2f}")
        print(f" -> Desconto de Faltas: R$ {payslip_1.absence_deduction:,.2f}")
        print(f" -> Salário Bruto a Pagar: R$ {payslip_1.net_salary:,.2f}")

    payslip_2 = payroll.get_payslip(emp_2.employee_id, "2026-05")
    if payslip_2:
        print(f"\nHolerite de {emp_2.name} (Mês: {payslip_2.month}):")
        print(f" -> Salário Base: R$ {payslip_2.base_salary:,.2f}")
        print(f" -> Horas Extras: R$ {payslip_2.overtime_pay:,.2f}")
        print(f" -> Desconto de 2 Faltas: R$ {payslip_2.absence_deduction:,.2f}")
        print(f" -> Salário Bruto a Pagar: R$ {payslip_2.net_salary:,.2f}")

    # --------------------------------------------------------------------------
    # CENÁRIO 4: Avaliação de Desempenho e Metas (Módulo Performance)
    # --------------------------------------------------------------------------
    print("\n--- CENÁRIO 4: Avaliação de Desempenho 360° (Módulo Performance) ---")
    rev_1 = performance.submit_review(SubmitReviewCommand(
        employee_id=emp_1.employee_id,
        reviewer_name="Diretoria de Engenharia",
        score=94.5,
        feedback="Entrega consistente da migração arquitetural com excelência técnica e mentoria da equipe.",
    ))
    print(f"Avaliação de {emp_1.name}:")
    print(f" -> Score: {rev_1.score}/100 | Classificação: {rev_1.rating}")
    print(f" -> Feedback: \"{rev_1.feedback}\"")

    rev_2 = performance.submit_review(SubmitReviewCommand(
        employee_id=emp_2.employee_id,
        reviewer_name="Diretoria de Produtos",
        score=82.0,
        feedback="Excelente liderança de produto e refinamento de backlog com os stakeholders.",
    ))
    print(f"\nAvaliação de {emp_2.name}:")
    print(f" -> Score: {rev_2.score}/100 | Classificação: {rev_2.rating}")
    print(f" -> Feedback: \"{rev_2.feedback}\"")

    print("\n" + "=" * 80)
    print(" Exemplo 06 de Modular Monolith finalizado com sucesso!")
    print("=" * 80)


if __name__ == "__main__":
    main()
