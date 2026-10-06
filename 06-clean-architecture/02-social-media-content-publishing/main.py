"""
main.py - Camada 4: Frameworks & Drivers (Composition Root).
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from entities.models import Author
from interface_adapters.gateways import (
    InMemoryAuthorRepository,
    InMemoryPostRepository,
    StaticModerationPolicyGateway,
)
from interface_adapters.presenters import JsonApiPostPresenter, MarkdownBlogPresenter
from interface_adapters.controllers import PostWebController
from use_cases.interactors import SubmitPostInteractor


def main() -> None:
    print("=" * 80)
    print(" CLEAN ARCHITECTURE - EXEMPLO 02: CONTENT PUBLISHING & MODERATION")
    print("=" * 80)

    # 1. Base de Autores e Repositórios (Infraestrutura)
    author_repo = InMemoryAuthorRepository({
        "usr_alice": Author(author_id="usr_alice", username="alice_dev", is_verified=True),
        "usr_bob": Author(author_id="usr_bob", username="bob_writer", is_verified=False),
        "usr_spammer": Author(author_id="usr_spammer", username="spam_bot", is_verified=False, is_banned=True),
    })
    post_repo = InMemoryPostRepository()
    moderation_gateway = StaticModerationPolicyGateway()

    # 2. Presenters distintos para demonstrar a separação do Output Boundary
    json_presenter = JsonApiPostPresenter()
    markdown_presenter = MarkdownBlogPresenter()

    # 3. Interactors conectados aos respectivos Presenters
    use_case_json = SubmitPostInteractor(
        author_repo=author_repo,
        post_repo=post_repo,
        moderation_policy=moderation_gateway,
        presenter=json_presenter,
    )
    use_case_markdown = SubmitPostInteractor(
        author_repo=author_repo,
        post_repo=post_repo,
        moderation_policy=moderation_gateway,
        presenter=markdown_presenter,
    )

    controller_json = PostWebController(use_case_json)
    controller_md = PostWebController(use_case_markdown)

    print("\n--- CENÁRIO 1: Publicação Válida via API REST (JSON Presenter) ---")
    controller_json.handle_create_post({
        "author_id": "usr_alice",
        "title": "Arquitetura Limpa na Prática em Python",
        "content": "A Clean Architecture permite desacoplar regras corporativas de detalhes de banco e web.",
        "tags": ["python", "architecture", "cleancode"],
    })
    print(f"HTTP Status: {json_presenter.status_code}")
    print(json.dumps(json_presenter.response_body, indent=2, ensure_ascii=False))

    print("\n--- CENÁRIO 2: O Mesmo Fluxo de Publicação Formatado para Blog Estático (Markdown Presenter) ---")
    controller_md.handle_create_post({
        "author_id": "usr_bob",
        "title": "Introdução ao Domain-Driven Design",
        "content": "Explorando Bounded Contexts, Agregados e Entidades no ecossistema moderno de software.",
        "tags": ["ddd", "software"],
    })
    print("Arquivo Markdown Gerado:")
    print(markdown_presenter.markdown_output)

    print("\n--- CENÁRIO 3: Violação de Moderação por Termo Proibido (Regra de Entidade) ---")
    controller_json.handle_create_post({
        "author_id": "usr_alice",
        "title": "Ganhe dinheiro rápido agora",
        "content": "Participe deste novo esquema de pirataria e duplique sua renda em dois dias.",
        "tags": ["renda"],
    })
    print(f"HTTP Status: {json_presenter.status_code}")
    print(json.dumps(json_presenter.response_body, indent=2, ensure_ascii=False))

    print("\n--- CENÁRIO 4: Tentativa de Publicação por Autor Suspenso (Regra de Caso de Uso) ---")
    controller_json.handle_create_post({
        "author_id": "usr_spammer",
        "title": "Post promocional não autorizado",
        "content": "Compre produtos com desconto extraordinário no nosso site exclusivo agora mesmo.",
        "tags": ["promocao"],
    })
    print(f"HTTP Status: {json_presenter.status_code}")
    print(json.dumps(json_presenter.response_body, indent=2, ensure_ascii=False))

    print("\n--- CENÁRIO 5: Consulta de Posts Aprovados no Repositório ---")
    published = post_repo.list_published()
    print(f"Total de posts ativos e aprovados: {len(published)}")
    for p in published:
        print(f" -> [{p.post_id}] \"{p.title}\" por @{p.author.username}")

    print("\n" + "=" * 80)
    print(" Exemplo 02 finalizado com sucesso!")
    print("=" * 80)


if __name__ == "__main__":
    main()
