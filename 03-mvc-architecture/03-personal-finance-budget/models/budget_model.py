"""
budget_model.py - Camada de Modelo (Model).

Gerencia as categorias orçamentárias, limites de gastos (tetos),
registro de despesas e cálculo de consumo percentual.
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional
import uuid


class ExpenseCategory(str, Enum):
    HOUSING = "MORADIA"
    FOOD = "ALIMENTAÇÃO"
    TRANSPORT = "TRANSPORTE"
    LEISURE = "LAZER"
    HEALTH = "SAÚDE"


@dataclass(frozen=True)
class Expense:
    expense_id: str
    category: ExpenseCategory
    description: str
    amount: float


@dataclass
class CategorySummary:
    category: ExpenseCategory
    budget_limit: float
    total_spent: float
    remaining: float
    spent_percentage: float
    is_over_budget: bool


class BudgetModel:
    def __init__(self, monthly_income: float) -> None:
        self.monthly_income = monthly_income
        self._limits: Dict[ExpenseCategory, float] = {}
        self._expenses: List[Expense] = []

    def set_category_limit(self, category: ExpenseCategory, limit: float) -> None:
        if limit < 0:
            raise ValueError("O teto da categoria não pode ser negativo.")
        self._limits[category] = limit

    def add_expense(self, category: ExpenseCategory, description: str, amount: float) -> Expense:
        if amount <= 0:
            raise ValueError("O valor da despesa deve ser positivo.")

        exp = Expense(
            expense_id=str(uuid.uuid4())[:8],
            category=category,
            description=description.strip(),
            amount=round(amount, 2),
        )
        self._expenses.append(exp)
        return exp

    def get_summaries(self) -> List[CategorySummary]:
        summaries: List[CategorySummary] = []
        for cat in ExpenseCategory:
            limit = self._limits.get(cat, 0.0)
            spent = sum(e.amount for e in self._expenses if e.category == cat)
            remaining = limit - spent
            pct = (spent / limit * 100) if limit > 0 else (100.0 if spent > 0 else 0.0)
            is_over = spent > limit if limit > 0 else spent > 0

            summaries.append(
                CategorySummary(
                    category=cat,
                    budget_limit=round(limit, 2),
                    total_spent=round(spent, 2),
                    remaining=round(remaining, 2),
                    spent_percentage=round(pct, 1),
                    is_over_budget=is_over,
                )
            )
        return summaries

    def get_overall_balance(self) -> Dict[str, float]:
        total_spent = sum(e.amount for e in self._expenses)
        total_budgeted = sum(self._limits.values())
        return {
            "income": self.monthly_income,
            "total_budgeted": round(total_budgeted, 2),
            "total_spent": round(total_spent, 2),
            "net_savings": round(self.monthly_income - total_spent, 2),
        }
