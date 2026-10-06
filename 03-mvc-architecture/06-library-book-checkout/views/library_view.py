"""
library_view.py - Camada de Visão (View).

Formata o catálogo do acervo bibliográfico, recibos de empréstimo e
comprovantes de devolução com cálculo de multa.
"""

from __future__ import annotations
from typing import List
from models.library_model import Book, Loan


class LibraryConsoleView:
    @staticmethod
    def render_catalog(books: List[Book]) -> None:
        print("\n" + "=" * 78)
        print("📚 BIBLIOTECA MUNICIPAL — CATÁLOGO DO ACERVO")
        print("=" * 78)
        header = f"{'ISBN':<14} | {'TÍTULO':<32} | {'AUTOR':<18} | DISPONÍVEL"
        print(header)
        print("-" * 78)
        for b in books:
            disp_str = f"{b.available_copies}/{b.total_copies} ex."
            status = "✅ DISPONÍVEL" if b.is_available else "❌ ESGOTADO"
            print(f"{b.isbn:<14} | {b.title[:30]:<32} | {b.author[:16]:<18} | {disp_str:<8} {status}")
        print("=" * 78)

    @staticmethod
    def render_loan_receipt(loan: Loan) -> None:
        print("\n" + "-" * 56)
        print("       COMPROVANTE DE EMPRÉSTIMO BIBLIOGRÁFICO")
        print("-" * 56)
        print(f" Código Empréstimo:   {loan.loan_id}")
        print(f" Usuário / Matrícula: {loan.user_id}")
        print(f" Livro:               {loan.book_title}")
        print(f" ISBN:                {loan.isbn}")
        print(f" Data de Retirada:    {loan.loan_date.strftime('%d/%m/%Y')}")
        print(f" Data Limite Devolução:{loan.due_date.strftime('%d/%m/%Y')}")
        print("-" * 56)
        print(" * Devoluções após o prazo estão sujeitas a multa diária.")
        print("-" * 56)

    @staticmethod
    def render_return_receipt(loan: Loan, days_late: int) -> None:
        print("\n" + "-" * 56)
        print("       COMPROVANTE DE DEVOLUÇÃO DE EXEMPLAR")
        print("-" * 56)
        print(f" Código Empréstimo:   {loan.loan_id}")
        print(f" Livro Devolvido:     {loan.book_title}")
        ret_date_str = loan.return_date.strftime('%d/%m/%Y') if loan.return_date else ""
        print(f" Data da Devolução:   {ret_date_str}")
        print(f" Dias de Atraso:      {days_late} dia(s)")
        if days_late > 0:
            fine_str = f"R$ {loan.fine_amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            print(f" ⚠️ MULTA INCORRIDA:    {fine_str} (Regularizar no balcão)")
        else:
            print(" ✅ Devolução no prazo! Nenhuma pendência financeira.")
        print("-" * 56)
