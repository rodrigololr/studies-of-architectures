"""
budget_controller.py - Camada de Controlador (Controller).

Recebe cadastros de limites orçamentários, adiciona despesas no Model
e comanda a renderização do relatório financeiro.
"""

from __future__ import annotations
from models.budget_model import BudgetModel, ExpenseCategory
from views.budget_view import BudgetConsoleView


class BudgetController:
    def __init__(self, model: BudgetModel) -> None:
        self.model = model
        self.view = BudgetConsoleView()

    def set_limit(self, category: ExpenseCategory, limit: float) -> None:
        self.model.set_category_limit(category, limit)

    def record_expense(self, category: ExpenseCategory, description: str, amount: float) -> str:
        exp = self.model.add_expense(category, description, amount)
        return exp.expense_id

    def display_budget_report(self) -> None:
        summaries = self.model.get_summaries()
        overall = self.model.get_overall_balance()
        self.view.render_report(summaries, overall)
