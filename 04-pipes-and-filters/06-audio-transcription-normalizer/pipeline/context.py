"""
context.py - Estruturas de dados de áudio transportadas no pipeline.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class AudioChunk:
    chunk_index: int
    start_second: float
    end_second: float
    transcription: Optional[str] = None


@dataclass
class AudioContext:
    audio_id: str
    filename: str
    audio_format: str
    sample_rate_hz: int
    duration_seconds: float
    silence_trimmed_seconds: float = 0.0
    effective_duration: float = 0.0
    noise_reduced: bool = False
    chunks: List[AudioChunk] = field(default_factory=list)
    final_transcript: str = ""
    is_valid: bool = True
    rejection_reason: Optional[str] = None
