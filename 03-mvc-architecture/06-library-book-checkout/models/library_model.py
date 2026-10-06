"""
library_model.py - Camada de Modelo (Model).

Modelos para acervo de livros, controle de exemplares, regras de empréstimo,
limites por usuário e cálculo de multa diária por atraso.
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import uuid


@dataclass
class Book:
    isbn: str
    title: str
    author: str
    total_copies: int
    available_copies: int

    @property
    def is_available(self) -> bool:
        return self.available_copies > 0


@dataclass
class Loan:
    loan_id: str
    user_id: str
    isbn: str
    book_title: str
    loan_date: datetime
    due_date: datetime
    return_date: Optional[datetime] = None
    fine_amount: float = 0.0

    @property
    def is_overdue(self) -> bool:
        check_date = self.return_date or datetime.now()
        return check_date > self.due_date


class LibraryModel:
    FINE_PER_DAY: float = 2.50  # R$ 2,50 por dia de atraso
    MAX_LOANS_PER_USER: int = 3
    LOAN_PERIOD_DAYS: int = 14

    def __init__(self) -> None:
        self._books: Dict[str, Book] = {}
        self._loans: Dict[str, Loan] = {}

    def add_book(self, isbn: str, title: str, author: str, copies: int) -> Book:
        book = Book(
            isbn=isbn.strip(),
            title=title.strip(),
            author=author.strip(),
            total_copies=copies,
            available_copies=copies,
        )
        self._books[isbn] = book
        return book

    def checkout_book(self, user_id: str, isbn: str) -> Loan:
        book = self._books.get(isbn)
        if not book:
            raise KeyError(f"Livro com ISBN '{isbn}' não cadastrado no acervo.")

        if not book.is_available:
            raise ValueError(f"Todos os exemplares do livro '{book.title}' estão atualmente emprestados.")

        # Valida limite de empréstimos simultâneos por usuário
        active_loans = [l for l in self._loans.values() if l.user_id == user_id and l.return_date is None]
        if len(active_loans) >= self.MAX_LOANS_PER_USER:
            raise ValueError(f"Usuário atingiu o limite máximo de {self.MAX_LOANS_PER_USER} empréstimos simultâneos.")

        # Valida se o usuário possui algum livro em atraso
        if any(l.is_overdue for l in active_loans):
            raise ValueError("Usuário possui livros com prazo de devolução vencido. Regularize as pendências primeiro.")

        book.available_copies -= 1
        now = datetime.now()
        due = now + timedelta(days=self.LOAN_PERIOD_DAYS)

        loan = Loan(
            loan_id=f"EMP-{str(uuid.uuid4())[:6].upper()}",
            user_id=user_id,
            isbn=isbn,
            book_title=book.title,
            loan_date=now,
            due_date=due,
        )
        self._loans[loan.loan_id] = loan
        return loan

    def return_book(self, loan_id: str, simulated_days_late: int = 0) -> Loan:
        loan = self._loans.get(loan_id)
        if not loan:
            raise KeyError(f"Empréstimo '{loan_id}' não localizado.")
        if loan.return_date is not None:
            raise ValueError("Este livro já foi devolvido anteriormente.")

        return_date = loan.due_date + timedelta(days=simulated_days_late)
        loan.return_date = return_date

        if simulated_days_late > 0:
            loan.fine_amount = round(simulated_days_late * self.FINE_PER_DAY, 2)

        book = self._books[loan.isbn]
        book.available_copies += 1
        return loan

    def get_catalog(self) -> List[Book]:
        return list(self._books.values())
