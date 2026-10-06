"""
header_validator_filter.py - Filtro 1: Validação de Formato e Taxa de Amostragem.

Garante que o áudio seja de formato aceito e possua qualidade mínima para transcrição (>= 8000 Hz).
"""

from __future__ import annotations
from typing import Optional
from pipeline.base import Filter
from pipeline.context import AudioContext


class AudioHeaderValidatorFilter(Filter[AudioContext, AudioContext]):
    ALLOWED_FORMATS = {"WAV", "MP3", "OGG", "FLAC", "M4A"}
    MIN_SAMPLE_RATE = 8000  # 8 kHz é o mínimo para telefonia/voz inteligível

    def process(self, ctx: AudioContext) -> Optional[AudioContext]:
        fmt = ctx.audio_format.upper().strip()
        if fmt not in self.ALLOWED_FORMATS:
            ctx.is_valid = False
            ctx.rejection_reason = f"Formato de áudio '{ctx.audio_format}' não é suportado."
            return ctx

        if ctx.sample_rate_hz < self.MIN_SAMPLE_RATE:
            ctx.is_valid = False
            ctx.rejection_reason = (
                f"Taxa de amostragem ({ctx.sample_rate_hz} Hz) insuficiente para IA de voz. "
                f"Mínimo exigido: {self.MIN_SAMPLE_RATE} Hz."
            )
            return ctx

        return ctx
