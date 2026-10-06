"""
server.py - Servidor Coletor de Telemetria com Detecção de Anomalias.

Recebe conexões simultâneas de sensores, calcula agregações em memória
e dispara alertas caso limiares críticos sejam excedidos.
"""

from __future__ import annotations
import socket
import threading
from typing import Callable, Dict, List, Optional
from protocol import TelemetryReading, TelemetryAck


class TelemetryCollectorServer:
    def __init__(
        self,
        alert_thresholds: Dict[str, float],
        host: str = "127.0.0.1",
        port: int = 0,
        on_alert: Optional[Callable[[str, str], None]] = None,
    ) -> None:
        self.alert_thresholds = alert_thresholds
        self.host = host
        self.port = port
        self.on_alert = on_alert
        self._server_socket: Optional[socket.socket] = None
        self._is_running = False
        self._lock = threading.Lock()
        # device_id -> lista de valores
        self._storage: Dict[str, List[float]] = {}

    @property
    def bound_port(self) -> int:
        if self._server_socket:
            return self._server_socket.getsockname()[1]
        return self.port

    def start(self) -> None:
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.bind((self.host, self.port))
        self._server_socket.listen(10)
        self._is_running = True

        threading.Thread(target=self._accept_loop, daemon=True).start()

    def _accept_loop(self) -> None:
        while self._is_running and self._server_socket:
            try:
                sock, _ = self._server_socket.accept()
                threading.Thread(target=self._handle_device, args=(sock,), daemon=True).start()
            except OSError:
                break

    def _handle_device(self, sock: socket.socket) -> None:
        buffer = ""
        try:
            while self._is_running:
                data = sock.recv(2048)
                if not data:
                    break

                buffer += data.decode("utf-8")
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    reading = TelemetryReading.deserialize(line)
                    if not reading:
                        continue

                    # Processa a leitura com thread-safety
                    with self._lock:
                        if reading.device_id not in self._storage:
                            self._storage[reading.device_id] = []
                        self._storage[reading.device_id].append(reading.value)

                    # Verifica limiar de anomalia
                    threshold = self.alert_thresholds.get(reading.metric)
                    alert_triggered = False
                    alert_msg = None

                    if threshold is not None and reading.value > threshold:
                        alert_triggered = True
                        alert_msg = (
                            f"ANOMALIA: Dispositivo {reading.device_id} registrou "
                            f"{reading.value} {reading.unit} (Limite: {threshold} {reading.unit})"
                        )
                        if self.on_alert:
                            self.on_alert(reading.device_id, alert_msg)

                    ack = TelemetryAck(
                        status="OK",
                        alert_triggered=alert_triggered,
                        alert_message=alert_msg,
                    )
                    sock.sendall(ack.serialize())
        except Exception:
            pass
        finally:
            try:
                sock.close()
            except OSError:
                pass

    def get_device_average(self, device_id: str) -> float:
        """Retorna a média aritmética dos valores registrados para o sensor."""
        with self._lock:
            readings = self._storage.get(device_id, [])
            return round(sum(readings) / len(readings), 2) if readings else 0.0

    def stop(self) -> None:
        self._is_running = False
        if self._server_socket:
            try:
                self._server_socket.close()
            except OSError:
                pass
