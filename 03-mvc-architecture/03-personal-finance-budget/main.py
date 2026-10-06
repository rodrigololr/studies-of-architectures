"""
main.py - Demonstração executável de Gestão Orçamentária Pessoal (Padrão MVC).

Configura renda mensal, define limites por categoria, insere despesas
e gera o relatório financeiro com indicadores visuais de consumo e estouro.
"""

from models.budget_model import BudgetModel, ExpenseCategory
from controllers.budget_controller import BudgetController


def main() -> None:
    print("=" * 80)
    print("DEMONSTRAÇÃO: Arquitetura MVC (Gestão Orçamentária Pessoal)")
    print("=" * 80)

    # 1. Instanciação dos componentes MVC com renda de R$ 8.000,00
    model = BudgetModel(monthly_income=8000.0)
    controller = BudgetController(model)

    # 2. Definição dos tetos de gastos por categoria
    controller.set_limit(ExpenseCategory.HOUSING, 2500.0)
    controller.set_limit(ExpenseCategory.FOOD, 1500.0)
    controller.set_limit(ExpenseCategory.TRANSPORT, 800.0)
    controller.set_limit(ExpenseCategory.HEALTH, 600.0)
    controller.set_limit(ExpenseCategory.LEISURE, 500.0)

    # 3. Lançamento de despesas ao longo do mês
    controller.record_expense(ExpenseCategory.HOUSING, "Aluguel e Condomínio", 2450.0)
    controller.record_expense(ExpenseCategory.FOOD, "Supermercado Semanal 1", 380.0)
    controller.record_expense(ExpenseCategory.FOOD, "Supermercado Semanal 2", 420.0)
    controller.record_expense(ExpenseCategory.FOOD, "Restaurante Final de Semana", 250.0)
    controller.record_expense(ExpenseCategory.TRANSPORT, "Combustível e Uber", 450.0)
    controller.record_expense(ExpenseCategory.HEALTH, "Farmácia e Vitaminas", 180.0)

    # Despesa de lazer que propositalmente estoura o teto planejado (R$ 680 de R$ 500)
    controller.record_expense(ExpenseCategory.LEISURE, "Show e Jantar", 680.0)

    # 4. Renderização da Visão Orçamentária
    controller.display_budget_report()


if __name__ == "__main__":
    main()
