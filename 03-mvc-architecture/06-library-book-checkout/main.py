"""
main.py - Demonstração executável de Empréstimo de Livros (Padrão MVC).

Cadastra acervo, exibe catálogo formatado, realiza empréstimos,
demonstra bloqueio de livro com exemplares esgotados e calcula multa por atraso na devolução.
"""

from models.library_model import LibraryModel
from controllers.library_controller import LibraryController


def main() -> None:
    print("=" * 65)
    print("DEMONSTRAÇÃO: Arquitetura MVC (Empréstimo de Livros e Multas)")
    print("=" * 65)

    # 1. Instanciação do MVC
    model = LibraryModel()
    controller = LibraryController(model)

    # 2. Cadastro de títulos no acervo
    controller.register_book("978-8575225431", "Clean Code: Habilidades Práticas", "Robert C. Martin", copies=2)
    controller.register_book("978-8575226766", "Domain-Driven Design", "Eric Evans", copies=1)
    controller.register_book("978-8575227244", "Refatoração: Aperfeiçoando o Código", "Martin Fowler", copies=1)

    # 3. Exibição do Catálogo
    controller.show_catalog()

    # 4. Empréstimo bem-sucedido para o leitor Rodrigo
    print("\n[AÇÃO 1] Realizando empréstimo de 'Domain-Driven Design' para Rodrigo...")
    controller.borrow_book(user_id="USR-RODRIGO-01", isbn="978-8575226766")

    # 5. Tentativa de empréstimo do mesmo livro por outro usuário (Esgotado)
    print("\n[AÇÃO 2] Outro usuário tentando o mesmo livro (Exemplar Único Esgotado)...")
    controller.borrow_book(user_id="USR-CARLOS-02", isbn="978-8575226766")

    # 6. Catálogo atualizado mostrando livro esgotado
    print("\n--- Catálogo Atualizado após Empréstimo ---")
    controller.show_catalog()

    # 7. Rodrigo devolve o livro com 4 dias de atraso (Multa: 4 * R$ 2,50 = R$ 10,00)
    # Recupera o ID do empréstimo ativo no modelo
    active_loan_id = list(model._loans.keys())[0]
    print(f"\n[AÇÃO 3] Devolvendo empréstimo '{active_loan_id}' com 4 dias de atraso...")
    controller.return_book(loan_id=active_loan_id, days_late=4)

    # 8. Catálogo volta a ter o livro disponível
    print("\n--- Catálogo Atualizado após Devolução ---")
    controller.show_catalog()


if __name__ == "__main__":
    main()
