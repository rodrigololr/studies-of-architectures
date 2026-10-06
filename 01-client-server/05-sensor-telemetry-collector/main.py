"""
main.py - Demonstração executável da Coleta de Telemetria IoT.

Inicializa o servidor coletor com limiares de alerta e simula
3 sensores enviando leituras periódicas em threads concorrentes.
"""

import time
import threading
from server import TelemetryCollectorServer
from client import SensorDeviceClient


def main() -> None:
    print("=" * 65)
    print("DEMONSTRAÇÃO: Coletor de Telemetria de Sensores IoT")
    print("=" * 65)

    # Limiares de alerta: temperatura > 75.0 °C, vibração > 50.0 mm/s
    thresholds = {"temperatura": 75.0, "vibracao": 50.0}

    alerts_received = []

    def on_alert_callback(device_id: str, message: str) -> None:
        alerts_received.append((device_id, message))
        print(f"  🚨 [ALERTA DISPARADO NO SERVIDOR] {message}")

    server = TelemetryCollectorServer(alert_thresholds=thresholds, port=0, on_alert=on_alert_callback)
    server.start()
    port = server.bound_port
    print(f"\n[SERVIDOR] TelemetryCollector ouvindo em 127.0.0.1:{port}")

    # Criação dos sensores clientes
    sensor_datacenter = SensorDeviceClient("sensor-dc-01", "temperatura", "°C", "127.0.0.1", port)
    sensor_motor = SensorDeviceClient("sensor-motor-a", "vibracao", "mm/s", "127.0.0.1", port)
    sensor_sala = SensorDeviceClient("sensor-sala-reuniao", "temperatura", "°C", "127.0.0.1", port)

    # Simulação de leituras normais
    print("\n--- Enviando Leituras de Operação Normal ---")
    ack1 = sensor_datacenter.send_reading(45.2)
    print(f"  [DC-01] Temp: 45.2°C -> Status ACK: {ack1.status if ack1 else 'Erro'}")

    ack2 = sensor_motor.send_reading(12.8)
    print(f"  [MOTOR-A] Vibração: 12.8 mm/s -> Status ACK: {ack2.status if ack2 else 'Erro'}")

    ack3 = sensor_sala.send_reading(23.5)
    print(f"  [SALA] Temp: 23.5°C -> Status ACK: {ack3.status if ack3 else 'Erro'}")

    # Simulação de leituras adicionais com anomalia crítica
    print("\n--- Enviando Leitura Crítica de Sobreaquecimento ---")
    ack_critico = sensor_datacenter.send_reading(82.6)  # Supera o limite de 75.0°C!
    if ack_critico and ack_critico.alert_triggered:
        print(f"  ⚠️ Sensor DC-01 recebeu confirmação de Alerta: {ack_critico.alert_message}")

    # Consulta de médias agregadas no servidor
    print("\n--- Métricas Agregadas no Servidor ---")
    avg_dc = server.get_device_average("sensor-dc-01")
    avg_motor = server.get_device_average("sensor-motor-a")
    print(f"  Média Histórica Sensor DC-01: {avg_dc} °C")
    print(f"  Média Histórica Sensor Motor-A: {avg_motor} mm/s")

    server.stop()
    print("\n[SERVIDOR] Servidor de telemetria encerrado.")
    print("=" * 65)


if __name__ == "__main__":
    main()
