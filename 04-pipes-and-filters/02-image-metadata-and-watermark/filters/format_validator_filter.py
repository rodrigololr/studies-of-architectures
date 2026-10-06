"""
format_validator_filter.py - Filtro 1: Validação de Formato e Extensão.

Bloqueia arquivos não suportados e scripts maliciosos disfarçados.
"""

from __future__ import annotations
from typing import Optional
from pipeline.base import Filter
from pipeline.context import ImagePayload


class FormatValidatorFilter(Filter[ImagePayload, ImagePayload]):
    ALLOWED_FORMATS = {"JPEG", "JPG", "PNG", "WEBP"}

    def process(self, image: ImagePayload) -> Optional[ImagePayload]:
        # Prevenção contra extensões duplas executáveis (ex: foto.php.jpg)
        lower_name = image.filename.lower()
        if any(ext in lower_name for ext in (".php", ".exe", ".sh", ".py", ".bat")):
            image.is_valid = False
            image.rejection_reason = "Arquivo rejeitado: extensão maliciosa suspeita detectada."
            return image

        fmt_upper = image.file_format.upper().strip()
        if fmt_upper not in self.ALLOWED_FORMATS:
            image.is_valid = False
            image.rejection_reason = f"Formato '{image.file_format}' não é suportado pelo portal."
            return image

        return image
