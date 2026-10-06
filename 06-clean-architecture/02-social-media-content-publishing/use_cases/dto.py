"""
use_cases/dto.py - Camada 2: DTOs para Moderação e Publicação de Posts.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class SubmitPostRequestModel:
    author_id: str
    title: str
    content: str
    tags: List[str]


@dataclass(frozen=True)
class SubmitPostResponseModel:
    success: bool
    post_id: Optional[str]
    author_username: Optional[str]
    title: Optional[str]
    status: str
    created_at: Optional[str]
    rejection_reason: Optional[str]
    message: str
