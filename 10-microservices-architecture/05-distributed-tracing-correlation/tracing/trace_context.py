"""W3C TraceContext & Span Data Structures (Padrão OpenTelemetry)."""

import uuid
import time
from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class Span:
    name: str
    service_name: str
    trace_id: str
    span_id: str
    parent_span_id: Optional[str] = None
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    duration_ms: float = 0.0
    attributes: Dict[str, Any] = field(default_factory=dict)
    status: str = "OK"  # "OK" ou "ERROR"
    error_message: Optional[str] = None

    def finish(self, status: str = "OK", error: Optional[str] = None) -> None:
        self.end_time = time.time()
        self.duration_ms = round((self.end_time - self.start_time) * 1000, 2)
        self.status = status
        self.error_message = error


class TraceContext:
    """Manipulador e propagador do cabeçalho oficial W3C 'traceparent'."""

    @staticmethod
    def generate_trace_id() -> str:
        return uuid.uuid4().hex

    @staticmethod
    def generate_span_id() -> str:
        return uuid.uuid4().hex[:16]

    @staticmethod
    def serialize_traceparent(trace_id: str, span_id: str, sampled: bool = True) -> str:
        flags = "01" if sampled else "00"
        return f"00-{trace_id}-{span_id}-{flags}"

    @staticmethod
    def parse_traceparent(header_value: str) -> Optional[Dict[str, str]]:
        # Formato esperado: 00-{trace_id}-{span_id}-{flags}
        parts = header_value.strip().split("-")
        if len(parts) == 4 and parts[0] == "00":
            return {
                "trace_id": parts[1],
                "parent_span_id": parts[2],
                "flags": parts[3],
            }
        return None
