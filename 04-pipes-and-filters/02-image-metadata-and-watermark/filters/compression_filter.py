"""
compression_filter.py - Filtro 5: Otimização e Compressão de Bytes.

Simula a re-codificação eficiente dos bytes para entrega rápida em CDN,
reduzindo a pegada de rede em 40%.
"""

from __future__ import annotations
from typing import Optional
from pipeline.base import Filter
from pipeline.context import ImagePayload


class CompressionOptimizationFilter(Filter[ImagePayload, ImagePayload]):
    def __init__(self, compression_ratio: float = 0.60) -> None:
        self.compression_ratio = compression_ratio

    def process(self, image: ImagePayload) -> Optional[ImagePayload]:
        if not image.is_valid:
            return image

        image.raw_size_bytes = int(round(image.raw_size_bytes * self.compression_ratio))
        image.is_optimized = True
        return image
