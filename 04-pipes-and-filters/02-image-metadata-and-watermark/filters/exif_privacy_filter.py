"""
exif_privacy_filter.py - Filtro 2: Remoção de Metadados EXIF e Proteção de Privacidade.

Remove coordenadas de GPS e modelo de câmera do usuário (conformidade com LGPD/GDPR).
"""

from __future__ import annotations
from typing import Optional
from pipeline.base import Filter
from pipeline.context import ImagePayload, ImageMetadata


class ExifPrivacyFilter(Filter[ImagePayload, ImagePayload]):
    def process(self, image: ImagePayload) -> Optional[ImagePayload]:
        if not image.is_valid:
            return image

        # Higieniza metadados eliminando geolocalização e identificadores físicos
        image.metadata = ImageMetadata(
            camera_model=None,
            gps_coordinates=None,
            created_at=image.metadata.created_at,  # Preserva data sem comprometer privacidade
        )
        return image
