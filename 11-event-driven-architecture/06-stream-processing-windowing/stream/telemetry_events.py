"""Eventos de Telemetria e Janelas de Stream Processing."""

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class SensorReadingEvent:
    sensor_id: str
    temperature_celsius: float
    timestamp_epoch: float  # Segundos


@dataclass(frozen=True)
class TumblingWindowSummary:
    window_start: float
    window_end: float
    sensor_id: str
    reading_count: int
    min_temp: float
    max_temp: float
    avg_temp: float


@dataclass(frozen=True)
class AnomalyAlertEvent:
    sensor_id: str
    detected_at: float
    threshold_limit: float
    actual_value: float
    severity: str  # "WARNING", "CRITICAL"
    reason: str
