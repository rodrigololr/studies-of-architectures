"""
chunker_filter.py - Filtro 4: Fatiamento em Chunks Menores.

Divide áudios longos em fatias de até 20 segundos para viabilizar
processamento paralelo e respeitar limites de modelos de fala.
"""

from __future__ import annotations
from typing import List, Optional
from pipeline.base import Filter
from pipeline.context import AudioContext, AudioChunk


class AudioChunkerFilter(Filter[AudioContext, AudioContext]):
    def __init__(self, max_chunk_duration: float = 20.0) -> None:
        self.max_chunk_duration = max_chunk_duration

    def process(self, ctx: AudioContext) -> Optional[AudioContext]:
        if not ctx.is_valid:
            return ctx

        duration = ctx.effective_duration
        chunks: List[AudioChunk] = []

        start = 0.0
        index = 1
        while start < duration:
            end = min(start + self.max_chunk_duration, duration)
            chunks.append(AudioChunk(chunk_index=index, start_second=start, end_second=end))
            start = end
            index += 1

        ctx.chunks = chunks
        return ctx
