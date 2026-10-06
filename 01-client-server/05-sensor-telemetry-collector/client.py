"""
client.py - Cliente Sensor IoT para envio de telemetria.

Conecta ao servidor coletor, transmite leituras e interpreta o ACK.
"""

from __future__ import annotations
from datetime import datetime
import socket
from typing import Optional
from protocol import TelemetryReading, TelemetryAck


class SensorDeviceClient:
    def __init__(self, device_id: str, metric: str, unit: str, host: str, port: int) -> None:
        self.device_id = device_id
        self.metric = metric
        self.unit = unit
        self.host = host
        self.port = port

    def send_reading(self, value: float) -> Optional[TelemetryAck]:
        """Envia uma leitura única para o servidor central e retorna o ACK recebido."""
        reading = TelemetryReading(
            device_id=self.device_id,
            metric=self.metric,
            value=value,
            unit=self.unit,
            timestamp=datetime.now().isoformat(),
        )

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2.0)
        sock.connect((self.host, self.port))

        try:
            sock.sendall(reading.serialize())

            buffer = ""
            while "\n" not in buffer:
                chunk = sock.recv(1024)
                if not chunk:
                    break
                buffer += chunk.decode("utf-8")

            line, _ = buffer.split("\n", 1)
            return TelemetryAck.deserialize(line)
        finally:
            sock.close()
