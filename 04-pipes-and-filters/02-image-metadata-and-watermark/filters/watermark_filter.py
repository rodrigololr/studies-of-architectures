"""
watermark_filter.py - Filtro 4: Aplicação de Marca D'Água.

Insere a marca d'água corporativa nos metadados visuais da imagem.
"""

from __future__ import annotations
from typing import Optional
from pipeline.base import Filter
from pipeline.context import ImagePayload


class WatermarkFilter(Filter[ImagePayload, ImagePayload]):
    def __init__(self, watermark_text: str = "© Estudos de Arquitetura") -> None:
        self.watermark_text = watermark_text

    def process(self, image: ImagePayload) -> Optional[ImagePayload]:
        if not image.is_valid:
            return image

        image.watermark_applied = True
        image.watermark_text = self.watermark_text
        return image
