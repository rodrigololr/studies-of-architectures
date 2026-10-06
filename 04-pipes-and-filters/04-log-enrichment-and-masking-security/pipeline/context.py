"""
context.py - Evento de Log enriquecido e transportado no pipeline.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class GeoLocation:
    country: str = "Desconhecido"
    city: str = "Desconhecida"


@dataclass
class LogEvent:
    raw_text: str
    timestamp: str = ""
    level: str = "INFO"
    service_name: str = ""
    client_ip: str = ""
    message: str = ""
    geo: GeoLocation = field(default_factory=GeoLocation)
    threat_detected: bool = False
    threat_type: Optional[str] = None
    is_valid: bool = True
    error_message: Optional[str] = None
