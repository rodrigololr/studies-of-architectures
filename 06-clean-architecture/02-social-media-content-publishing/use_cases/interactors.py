"""
use_cases/interactors.py - Camada 2: Interactors.
"""

from __future__ import annotations
import uuid
from datetime import datetime, timezone
from entities.models import Post, PostStatus
from use_cases.dto import SubmitPostRequestModel, SubmitPostResponseModel
from use_cases.boundaries import (
    SubmitPostInputBoundary,
    SubmitPostOutputBoundary,
    PostRepositoryGateway,
    AuthorRepositoryGateway,
    ModerationPolicyGateway,
)


class SubmitPostInteractor(SubmitPostInputBoundary):
    def __init__(
        self,
        author_repo: AuthorRepositoryGateway,
        post_repo: PostRepositoryGateway,
        moderation_policy: ModerationPolicyGateway,
        presenter: SubmitPostOutputBoundary,
    ) -> None:
        self.author_repo = author_repo
        self.post_repo = post_repo
        self.moderation_policy = moderation_policy
        self.presenter = presenter

    def execute(self, request: SubmitPostRequestModel) -> None:
        # 1. Validação de Autor
        author = self.author_repo.find_by_id(request.author_id)
        if not author:
            self.presenter.present(SubmitPostResponseModel(
                success=False,
                post_id=None,
                author_username=None,
                title=request.title,
                status=PostStatus.REJECTED.value,
                created_at=None,
                rejection_reason=f"Autor '{request.author_id}' não cadastrado no sistema.",
                message="Falha de autenticação do autor.",
            ))
            return

        if author.is_banned:
            self.presenter.present(SubmitPostResponseModel(
                success=False,
                post_id=None,
                author_username=author.username,
                title=request.title,
                status=PostStatus.REJECTED.value,
                created_at=None,
                rejection_reason="A conta do autor encontra-se suspensa por violação prévia de diretrizes.",
                message="Publicação bloqueada por suspensão cadastral.",
            ))
            return

        # 2. Instanciação da Entidade de Negócio
        post_id = f"post_{uuid.uuid4().hex[:8]}"
        now = datetime.now(timezone.utc)
        post = Post(
            post_id=post_id,
            author=author,
            title=request.title,
            content=request.content,
            tags=request.tags,
            status=PostStatus.DRAFT,
            created_at=now,
        )

        # 3. Execução da Regra de Moderação (Invocando a Entidade com a Política)
        forbidden_terms = self.moderation_policy.get_prohibited_terms()
        is_safe, violation_reason = post.moderate_content(forbidden_terms)

        if not is_safe:
            post.reject(violation_reason or "Violação de conteúdo")
            self.post_repo.save(post)
            self.presenter.present(SubmitPostResponseModel(
                success=False,
                post_id=post.post_id,
                author_username=author.username,
                title=post.title,
                status=post.status.value,
                created_at=post.created_at.strftime("%Y-%m-%d %H:%M:%S UTC"),
                rejection_reason=post.rejection_reason,
                message="Publicação rejeitada pelo motor de moderação.",
            ))
            return

        # 4. Publicação Aprovada
        post.publish(now)
        self.post_repo.save(post)

        # 5. Emissão para o Output Boundary (Presenter)
        self.presenter.present(SubmitPostResponseModel(
            success=True,
            post_id=post.post_id,
            author_username=author.username,
            title=post.title,
            status=post.status.value,
            created_at=post.published_at.strftime("%Y-%m-%d %H:%M:%S UTC") if post.published_at else "",
            rejection_reason=None,
            message="Post aprovado na moderação e publicado com sucesso!",
        ))
