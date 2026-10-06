"""
entities/models.py - Camada 1: Entities (Enterprise Business Rules).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional, Tuple


class PostStatus(str, Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class Author:
    author_id: str
    username: str
    is_verified: bool
    is_banned: bool = False


@dataclass
class Post:
    post_id: str
    author: Author
    title: str
    content: str
    tags: List[str]
    status: PostStatus
    created_at: datetime
    published_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None

    def moderate_content(self, forbidden_words: List[str]) -> Tuple[bool, Optional[str]]:
        """
        Regra Corporativa de Negócio:
        Avalia conformidade de comprimento mínimo e sanitização de vocabulário ofensivo.
        """
        if len(self.title.strip()) < 5:
            return False, "Título muito curto (mínimo de 5 caracteres)."

        if len(self.content.strip()) < 20:
            return False, "Conteúdo insuficiente (mínimo de 20 caracteres)."

        full_text = f"{self.title} {self.content}".lower()
        for bad_word in forbidden_words:
            if bad_word.lower() in full_text:
                return False, f"Conteúdo viola os termos de uso por conter linguagem imprópria: '{bad_word}'"

        return True, None

    def publish(self, now: datetime) -> None:
        self.status = PostStatus.PUBLISHED
        self.published_at = now
        self.rejection_reason = None

    def reject(self, reason: str) -> None:
        self.status = PostStatus.REJECTED
        self.rejection_reason = reason
