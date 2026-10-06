"""Tumbling Window Aggregator (Janelas Temporais Fixas e Não Sobrepostas)."""

from typing import List, Dict, Optional
from stream.telemetry_events import SensorReadingEvent, TumblingWindowSummary


class TumblingWindowAggregator:
    """Agrega eventos em intervalos de tempo discretos sem sobreposição [T, T + size)."""

    def __init__(self, window_size_seconds: float = 5.0) -> None:
        self.window_size = window_size_seconds
        self._current_window_start: Optional[float] = None
        self._buffer: List[SensorReadingEvent] = []
        self.completed_windows: List[TumblingWindowSummary] = []

    def ingest(self, event: SensorReadingEvent) -> Optional[TumblingWindowSummary]:
        if self._current_window_start is None:
            # Inicializa a primeira janela com base no timestamp do primeiro evento
            self._current_window_start = float(int(event.timestamp_epoch // self.window_size) * self.window_size)

        current_window_end = self._current_window_start + self.window_size

        summary = None
        # Se o evento chegou após o fechamento da janela atual, fecha a janela
        while event.timestamp_epoch >= current_window_end:
            summary = self._close_window(current_window_end)
            if summary:
                self.completed_windows.append(summary)
            # Avança a janela
            self._current_window_start = current_window_end
            current_window_end = self._current_window_start + self.window_size

        self._buffer.append(event)
        return summary

    def flush(self) -> Optional[TumblingWindowSummary]:
        """Força o fechamento da janela aberta atual."""
        if not self._buffer or self._current_window_start is None:
            return None
        summary = self._close_window(self._current_window_start + self.window_size)
        if summary:
            self.completed_windows.append(summary)
        return summary

    def _close_window(self, window_end: float) -> Optional[TumblingWindowSummary]:
        if not self._buffer or self._current_window_start is None:
            return None

        sensor_id = self._buffer[0].sensor_id
        temps = [e.temperature_celsius for e in self._buffer]
        summary = TumblingWindowSummary(
            window_start=self._current_window_start,
            window_end=window_end,
            sensor_id=sensor_id,
            reading_count=len(temps),
            min_temp=round(min(temps), 2),
            max_temp=round(max(temps), 2),
            avg_temp=round(sum(temps) / len(temps), 2),
        )
        self._buffer.clear()
        return summary
