"""
protocol.py - Protocolo de Telemetria IoT e Confirmação de Recepção (ACK).

Modela o envio periódico de métricas por sensores industriais para um servidor central.
"""

from __future__ import annotations
from dataclasses import dataclass
import json
from typing import Optional


@dataclass(frozen=True)
class TelemetryReading:
    device_id: str
    metric: str
    value: float
    unit: str
    timestamp: str

    def serialize(self) -> bytes:
        payload = {
            "device_id": self.device_id,
            "metric": self.metric,
            "value": self.value,
            "unit": self.unit,
            "timestamp": self.timestamp,
        }
        return (json.dumps(payload) + "\n").encode("utf-8")

    @classmethod
    def deserialize(cls, raw_line: str) -> Optional[TelemetryReading]:
        try:
            data = json.loads(raw_line.strip())
            return cls(
                device_id=data["device_id"],
                metric=data["metric"],
                value=float(data["value"]),
                unit=data["unit"],
                timestamp=data["timestamp"],
            )
        except Exception:
            return None


@dataclass(frozen=True)
class TelemetryAck:
    status: str
    alert_triggered: bool
    alert_message: Optional[str] = None

    def serialize(self) -> bytes:
        payload = {
            "status": self.status,
            "alert": self.alert_triggered,
            "alert_message": self.alert_message,
        }
        return (json.dumps(payload) + "\n").encode("utf-8")

    @classmethod
    def deserialize(cls, raw_line: str) -> Optional[TelemetryAck]:
        try:
            data = json.loads(raw_line.strip())
            return cls(
                status=data["status"],
                alert_triggered=bool(data["alert"]),
                alert_message=data.get("alert_message"),
            )
        except Exception:
            return None
