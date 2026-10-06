"""
interface_adapters/gateways.py - Camada 3: Gateways & Repositórios.
"""

from __future__ import annotations
from typing import Dict, Optional, List
from entities.models import Post, Author, PostStatus
from use_cases.boundaries import (
    PostRepositoryGateway,
    AuthorRepositoryGateway,
    ModerationPolicyGateway,
)


class InMemoryPostRepository(PostRepositoryGateway):
    def __init__(self) -> None:
        self._posts: Dict[str, Post] = {}

    def save(self, post: Post) -> None:
        self._posts[post.post_id] = post

    def find_by_id(self, post_id: str) -> Optional[Post]:
        return self._posts.get(post_id)

    def list_published(self) -> List[Post]:
        return [p for p in self._posts.values() if p.status == PostStatus.PUBLISHED]


class InMemoryAuthorRepository(AuthorRepositoryGateway):
    def __init__(self, authors: Optional[Dict[str, Author]] = None) -> None:
        self._authors: Dict[str, Author] = dict(authors or {})

    def find_by_id(self, author_id: str) -> Optional[Author]:
        return self._authors.get(author_id)


class StaticModerationPolicyGateway(ModerationPolicyGateway):
    def __init__(self, prohibited_terms: Optional[List[str]] = None) -> None:
        self._terms = prohibited_terms or [
            "fraude",
            "pirataria",
            "golpe",
            "spam",
            "ofensivo",
        ]

    def get_prohibited_terms(self) -> List[str]:
        return list(self._terms)
