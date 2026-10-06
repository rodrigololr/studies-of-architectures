"""
silence_trimmer_filter.py - Filtro 2: Remoção de Silêncio Inicial e Final.

Detecta e remove segundos mortos de silêncio para otimizar tempo e custo de IA.
"""

from __future__ import annotations
from typing import Optional
from pipeline.base import Filter
from pipeline.context import AudioContext


class SilenceTrimmerFilter(Filter[AudioContext, AudioContext]):
    def __init__(self, simulated_trim_seconds: float = 3.0) -> None:
        self.simulated_trim_seconds = simulated_trim_seconds

    def process(self, ctx: AudioContext) -> Optional[AudioContext]:
        if not ctx.is_valid:
            return ctx

        # Se o áudio tiver mais de 10 segundos, simula que havia silêncio no início/fim
        trim = min(self.simulated_trim_seconds, max(0.0, ctx.duration_seconds - 5.0))
        ctx.silence_trimmed_seconds = round(trim, 1)
        ctx.effective_duration = round(ctx.duration_seconds - trim, 1)

        return ctx
