"""
context.py - Estrutura de dados da imagem que trafega pelos dutos.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class ImageMetadata:
    camera_model: Optional[str] = None
    gps_coordinates: Optional[str] = None
    created_at: Optional[str] = None


@dataclass
class ImagePayload:
    filename: str
    file_format: str
    raw_size_bytes: int
    width: int
    height: int
    metadata: ImageMetadata
    watermark_applied: bool = False
    watermark_text: Optional[str] = None
    is_optimized: bool = False
    is_valid: bool = True
    rejection_reason: Optional[str] = None
