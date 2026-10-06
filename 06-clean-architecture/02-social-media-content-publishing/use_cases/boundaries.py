"""
use_cases/boundaries.py - Camada 2: Boundaries e Gateways.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, List
from entities.models import Post, Author
from use_cases.dto import SubmitPostRequestModel, SubmitPostResponseModel


class SubmitPostInputBoundary(ABC):
    @abstractmethod
    def execute(self, request: SubmitPostRequestModel) -> None:
        pass


class SubmitPostOutputBoundary(ABC):
    @abstractmethod
    def present(self, response: SubmitPostResponseModel) -> None:
        pass


class PostRepositoryGateway(ABC):
    @abstractmethod
    def save(self, post: Post) -> None:
        pass

    @abstractmethod
    def find_by_id(self, post_id: str) -> Optional[Post]:
        pass

    @abstractmethod
    def list_published(self) -> List[Post]:
        pass


class AuthorRepositoryGateway(ABC):
    @abstractmethod
    def find_by_id(self, author_id: str) -> Optional[Author]:
        pass


class ModerationPolicyGateway(ABC):
    @abstractmethod
    def get_prohibited_terms(self) -> List[str]:
        pass
