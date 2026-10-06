"""
domain/services/tax_calculator.py - Camada 2: Domain Services.

Motor de cálculo tributário e trabalhista progressivo (INSS, IRPF e benefícios).
Lógica pura de domínio sem dependência de banco de dados ou web.
"""

from __future__ import annotations
from domain.model.employee import Employee


class BrazilianLaborTaxCalculatorService:
    @staticmethod
    def calculate_inss(gross_salary: float) -> float:
        """
        Cálculo progressivo das alíquotas do INSS por faixas salariais:
        - Faixa 1 (até R$ 1.412,00): 7.5%
        - Faixa 2 (R$ 1.412,01 a R$ 2.666,68): 9%
        - Faixa 3 (R$ 2.666,69 a R$ 4.000,03): 12%
        - Faixa 4 (R$ 4.000,04 a R$ 7.786,02): 14%
        - Teto máximo do INSS: R$ 908,86
        """
        inss_total = 0.0

        # Faixa 1
        if gross_salary <= 1412.00:
            return round(gross_salary * 0.075, 2)
        inss_total += 1412.00 * 0.075

        # Faixa 2
        if gross_salary <= 2666.68:
            return round(inss_total + ((gross_salary - 1412.00) * 0.09), 2)
        inss_total += (2666.68 - 1412.00) * 0.09

        # Faixa 3
        if gross_salary <= 4000.03:
            return round(inss_total + ((gross_salary - 2666.68) * 0.12), 2)
        inss_total += (4000.03 - 2666.68) * 0.12

        # Faixa 4 (até o teto de R$ 7.786,02)
        if gross_salary <= 7786.02:
            return round(inss_total + ((gross_salary - 4000.03) * 0.14), 2)
        inss_total += (7786.02 - 4000.03) * 0.14

        # Teto Máximo
        return round(inss_total, 2)

    @staticmethod
    def calculate_irpf(gross_salary: float, inss_deduction: float, dependents_count: int) -> float:
        """
        Cálculo do IRPF progressivo sobre a base líquida:
        Base = Salário Bruto - INSS - (Dependentes * R$ 189,59)
        """
        dependent_deduction = dependents_count * 189.59
        base_calculo = gross_salary - inss_deduction - dependent_deduction

        if base_calculo <= 2259.20:
            return 0.0
        elif base_calculo <= 2826.65:
            imposto = (base_calculo * 0.075) - 169.44
        elif base_calculo <= 3751.05:
            imposto = (base_calculo * 0.150) - 381.44
        elif base_calculo <= 4664.68:
            imposto = (base_calculo * 0.225) - 662.77
        else:
            imposto = (base_calculo * 0.275) - 896.00

        return round(max(0.0, imposto), 2)

    @staticmethod
    def calculate_benefits(employee: Employee) -> float:
        """
        Desconto de Vale-Refeição de até 6% do salário base ou teto de R$ 180,00.
        """
        if not employee.meal_voucher_opt_in:
            return 0.0
        return round(min(employee.base_salary * 0.06, 180.00), 2)
