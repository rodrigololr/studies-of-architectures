"""Sliding Window Anomaly Detector (Janela Deslizante Contínua para Detecção de Picos)."""

from typing import List, Optional
from stream.telemetry_events import SensorReadingEvent, AnomalyAlertEvent


class SlidingWindowAnomalyDetector:
    """Mantém uma janela deslizante contínua dos últimos N segundos para detectar anomalias."""

    def __init__(
        self,
        window_duration_seconds: float = 5.0,
        critical_temp_threshold: float = 85.0,
    ) -> None:
        self.window_duration = window_duration_seconds
        self.critical_threshold = critical_temp_threshold
        self._sliding_buffer: List[SensorReadingEvent] = []
        self.generated_alerts: List[AnomalyAlertEvent] = []

    def ingest(self, event: SensorReadingEvent) -> Optional[AnomalyAlertEvent]:
        self._sliding_buffer.append(event)

        # Expulsa eventos mais velhos que a cauda da janela deslizante: (T_atual - window_duration)
        cutoff_time = event.timestamp_epoch - self.window_duration
        self._sliding_buffer = [e for e in self._sliding_buffer if e.timestamp_epoch >= cutoff_time]

        # Avaliação de anomalia na janela deslizante atual
        if event.temperature_celsius >= self.critical_threshold:
            alert = AnomalyAlertEvent(
                sensor_id=event.sensor_id,
                detected_at=event.timestamp_epoch,
                threshold_limit=self.critical_threshold,
                actual_value=event.temperature_celsius,
                severity="CRITICAL",
                reason=f"Superaquecimento detectado: {event.temperature_celsius}°C excede o limite de {self.critical_threshold}°C na janela móvel de {self.window_duration}s",
            )
            self.generated_alerts.append(alert)
            return alert

        return None

    def get_current_window_readings(self) -> List[SensorReadingEvent]:
        return list(self._sliding_buffer)
