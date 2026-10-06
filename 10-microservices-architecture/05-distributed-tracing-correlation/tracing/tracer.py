"""Tracer e Coletor Centralizado de Spans (Jaeger / Zipkin Simulator)."""

import contextlib
from typing import Dict, List, Optional, Generator
from tracing.trace_context import Span, TraceContext


class InMemorySpanCollector:
    """Coletor central de telemetria distribuída."""

    def __init__(self) -> None:
        self._spans: List[Span] = []

    def record_span(self, span: Span) -> None:
        self._spans.append(span)

    def get_trace_tree(self, trace_id: str) -> List[Span]:
        matching = [s for s in self._spans if s.trace_id == trace_id]
        return sorted(matching, key=lambda s: s.start_time)


class Tracer:
    """Instrumentador de microsserviços para criação e propagação de Spans."""

    def __init__(self, service_name: str, collector: InMemorySpanCollector) -> None:
        self.service_name = service_name
        self.collector = collector

    @contextlib.contextmanager
    def start_span(
        self,
        span_name: str,
        incoming_headers: Optional[Dict[str, str]] = None,
    ) -> Generator[Span, None, None]:
        headers = incoming_headers or {}
        traceparent = headers.get("traceparent")

        if traceparent:
            parsed = TraceContext.parse_traceparent(traceparent)
            if parsed:
                trace_id = parsed["trace_id"]
                parent_span_id = parsed["parent_span_id"]
            else:
                trace_id = TraceContext.generate_trace_id()
                parent_span_id = None
        else:
            # Raiz do Trace
            trace_id = TraceContext.generate_trace_id()
            parent_span_id = None

        current_span_id = TraceContext.generate_span_id()
        span = Span(
            name=span_name,
            service_name=self.service_name,
            trace_id=trace_id,
            span_id=current_span_id,
            parent_span_id=parent_span_id,
        )

        try:
            yield span
            span.finish(status="OK")
        except Exception as exc:
            span.finish(status="ERROR", error=str(exc))
            raise exc
        finally:
            self.collector.record_span(span)

    def inject_context(self, span: Span, headers: Dict[str, str]) -> Dict[str, str]:
        """Injeta o cabeçalho 'traceparent' para ser propagado na chamada HTTP downstream."""
        headers["traceparent"] = TraceContext.serialize_traceparent(
            span.trace_id, span.span_id
        )
        return headers
