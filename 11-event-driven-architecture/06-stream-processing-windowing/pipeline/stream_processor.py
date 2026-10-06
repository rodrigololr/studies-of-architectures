"""Stream Processing Engine coordenando operadores de janela."""

from typing import Dict, Any, List, Optional
from stream.telemetry_events import SensorReadingEvent, TumblingWindowSummary, AnomalyAlertEvent
from stream.tumbling_window import TumblingWindowAggregator
from stream.sliding_window import SlidingWindowAnomalyDetector


class StreamProcessingPipeline:
    """Pipeline reativo de processamento de fluxos em tempo real (Kafka Streams / Flink Pattern)."""

    def __init__(
        self,
        tumbling_window_seconds: float = 5.0,
        sliding_window_seconds: float = 5.0,
        anomaly_threshold: float = 85.0,
    ) -> None:
        self.tumbling = TumblingWindowAggregator(tumbling_window_seconds)
        self.sliding = SlidingWindowAnomalyDetector(sliding_window_seconds, anomaly_threshold)

    def process_event(self, event: SensorReadingEvent) -> Dict[str, Any]:
        closed_tumbling = self.tumbling.ingest(event)
        anomaly_alert = self.sliding.ingest(event)

        return {
            "sensor_id": event.sensor_id,
            "current_temp": event.temperature_celsius,
            "timestamp": event.timestamp_epoch,
            "tumbling_window_emitted": closed_tumbling,
            "anomaly_detected": anomaly_alert,
        }

    def flush_pipeline(self) -> Optional[TumblingWindowSummary]:
        return self.tumbling.flush()
