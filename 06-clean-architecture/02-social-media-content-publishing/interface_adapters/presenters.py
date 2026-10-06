"""
interface_adapters/presenters.py - Camada 3: Presenters.

Demonstra o poder da Clean Architecture: o mesmo caso de uso alimenta tanto
um apresentador de API REST JSON quanto um gerador de Markdown estático.
"""

from __future__ import annotations
from typing import Dict, Any, Optional
from use_cases.dto import SubmitPostResponseModel
from use_cases.boundaries import SubmitPostOutputBoundary


class JsonApiPostPresenter(SubmitPostOutputBoundary):
    def __init__(self) -> None:
        self.status_code: int = 200
        self.response_body: Dict[str, Any] = {}

    def present(self, response: SubmitPostResponseModel) -> None:
        if response.success:
            self.status_code = 201
            self.response_body = {
                "status": "SUCCESS",
                "post": {
                    "id": response.post_id,
                    "title": response.title,
                    "author": response.author_username,
                    "publication_state": response.status,
                    "published_at": response.created_at,
                },
                "meta": {"message": response.message},
            }
        else:
            self.status_code = 422
            self.response_body = {
                "status": "UNPROCESSABLE_ENTITY",
                "rejection_reason": response.rejection_reason,
                "meta": {"message": response.message},
            }


class MarkdownBlogPresenter(SubmitPostOutputBoundary):
    def __init__(self) -> None:
        self.markdown_output: str = ""

    def present(self, response: SubmitPostResponseModel) -> None:
        if response.success:
            self.markdown_output = (
                f"---\n"
                f"title: \"{response.title}\"\n"
                f"author: \"{response.author_username}\"\n"
                f"date: \"{response.created_at}\"\n"
                f"post_id: \"{response.post_id}\"\n"
                f"layout: post\n"
                f"---\n\n"
                f"# {response.title}\n\n"
                f"*Publicado oficialmente por @{response.author_username} sob licença CC-BY.*\n"
            )
        else:
            self.markdown_output = (
                f"> ⚠️ **[BLOQUEADO] Publicação Recusada**\n"
                f"> Motivo da Moderação: {response.rejection_reason}\n"
            )
