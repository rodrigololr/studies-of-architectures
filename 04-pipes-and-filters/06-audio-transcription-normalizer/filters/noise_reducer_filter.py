"""
noise_reducer_filter.py - Filtro 3: Redução de Ruído de Fundo.

Simula aplicação de filtro passa-baixa e subtração espectral para elevar nitidez da voz.
"""

from __future__ import annotations
from typing import Optional
from pipeline.base import Filter
from pipeline.context import AudioContext


class NoiseReductionFilter(Filter[AudioContext, AudioContext]):
    def process(self, ctx: AudioContext) -> Optional[AudioContext]:
        if not ctx.is_valid:
            return ctx

        ctx.noise_reduced = True
        return ctx
