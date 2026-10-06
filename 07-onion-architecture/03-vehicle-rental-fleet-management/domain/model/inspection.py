"""
domain/model/inspection.py - Camada 1: Domain Model.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List


@dataclass(frozen=True)
class InspectionReport:
    odometer_km: float
    fuel_level_eighths: int  # 0 a 8
    damages: List[str] = field(default_factory=list)
    inspected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
