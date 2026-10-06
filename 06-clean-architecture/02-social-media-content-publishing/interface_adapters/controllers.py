"""
interface_adapters/controllers.py - Camada 3: Controllers.
"""

from __future__ import annotations
from typing import Dict, Any
from use_cases.dto import SubmitPostRequestModel
from use_cases.boundaries import SubmitPostInputBoundary


class PostWebController:
    def __init__(self, submit_post_use_case: SubmitPostInputBoundary) -> None:
        self.submit_post_use_case = submit_post_use_case

    def handle_create_post(self, payload: Dict[str, Any]) -> None:
        req = SubmitPostRequestModel(
            author_id=payload.get("author_id", ""),
            title=payload.get("title", ""),
            content=payload.get("content", ""),
            tags=payload.get("tags", []),
        )
        self.submit_post_use_case.execute(req)
