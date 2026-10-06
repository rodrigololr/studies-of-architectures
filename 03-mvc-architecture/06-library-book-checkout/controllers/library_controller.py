"""
library_controller.py - Camada de Controlador (Controller).

Intermedeia os comandos de acervo, empréstimo e devolução,
tratando erros de indisponibilidade e comandando a renderização.
"""

from __future__ import annotations
from models.library_model import LibraryModel
from views.library_view import LibraryConsoleView


class LibraryController:
    def __init__(self, model: LibraryModel) -> None:
        self.model = model
        self.view = LibraryConsoleView()

    def register_book(self, isbn: str, title: str, author: str, copies: int) -> None:
        self.model.add_book(isbn, title, author, copies)

    def show_catalog(self) -> None:
        books = self.model.get_catalog()
        self.view.render_catalog(books)

    def borrow_book(self, user_id: str, isbn: str) -> None:
        try:
            loan = self.model.checkout_book(user_id, isbn)
            self.view.render_loan_receipt(loan)
        except (ValueError, KeyError) as ex:
            print(f"\n❌ [EMPRÉSTIMO RECUSADO]: {ex}")

    def return_book(self, loan_id: str, days_late: int = 0) -> None:
        try:
            loan = self.model.return_book(loan_id, simulated_days_late=days_late)
            self.view.render_return_receipt(loan, days_late)
        except (ValueError, KeyError) as ex:
            print(f"\n❌ [ERRO NA DEVOLUÇÃO]: {ex}")
