"""
resolution_resize_filter.py - Filtro 3: Redimensionamento e Padronização.

Redimensiona imagens com resolução acima do limite máximo (ex: 1920x1080)
mantendo a proporção de aspecto (aspect ratio).
"""

from __future__ import annotations
from typing import Optional
from pipeline.base import Filter
from pipeline.context import ImagePayload


class ResolutionResizeFilter(Filter[ImagePayload, ImagePayload]):
    def __init__(self, max_width: int = 1920, max_height: int = 1080) -> None:
        self.max_width = max_width
        self.max_height = max_height

    def process(self, image: ImagePayload) -> Optional[ImagePayload]:
        if not image.is_valid:
            return image

        if image.width > self.max_width or image.height > self.max_height:
            scale_w = self.max_width / image.width
            scale_h = self.max_height / image.height
            scale = min(scale_w, scale_h)

            image.width = int(round(image.width * scale))
            image.height = int(round(image.height * scale))

        return image
