"""Demonstração de EDA: Stream Processing & Time Windowing (Tumbling e Sliding Windows).

Cenários demonstrados:
1. Ingestão de fluxo contínuo de telemetria IoT (leituras nominais de temperatura)
2. Fechamento automático de Janela de Salto (Tumbling Window de 5 segundos) com métricas agregadas (mín, máx, média)
3. Detecção em tempo real de anomalia de superaquecimento na Janela Deslizante (Sliding Window)
4. Fechamento da segunda Janela Tumbling capturando o pico histórico
5. Auditoria e métricas do pipeline de streaming
"""

import sys
from pathlib import Path

# Garante resolução de imports absolutos
sys.path.insert(0, str(Path(__file__).parent))

from stream.telemetry_events import SensorReadingEvent
from pipeline.stream_processor import StreamProcessingPipeline


def print_separator(title: str) -> None:
    print(f"\n{'='*75}\n>>> {title}\n{'='*75}")


def main() -> None:
    print("Inicializando Pipeline de Stream Processing e Operadores de Janela Temporal...")

    # Pipeline configurado: Janelas de 5 segundos e limiar crítico de 85.0°C
    pipeline = StreamProcessingPipeline(
        tumbling_window_seconds=5.0,
        sliding_window_seconds=5.0,
        anomaly_threshold=85.0,
    )

    # -------------------------------------------------------------------------
    # Cenário 1: Ingestão do Fluxo Inicial [t = 0.0s até t = 4.0s]
    # -------------------------------------------------------------------------
    print_separator("Cenário 1: Ingestão de 5 Leituras Nominais na 1ª Janela [0.0s - 5.0s)")
    stream_batch_1 = [
        SensorReadingEvent("SENSOR-TURBINE-01", 40.5, 0.0),
        SensorReadingEvent("SENSOR-TURBINE-01", 41.2, 1.0),
        SensorReadingEvent("SENSOR-TURBINE-01", 42.0, 2.0),
        SensorReadingEvent("SENSOR-TURBINE-01", 40.8, 3.0),
        SensorReadingEvent("SENSOR-TURBINE-01", 41.5, 4.0),
    ]

    for reading in stream_batch_1:
        res = pipeline.process_event(reading)
        print(f"  [t={reading.timestamp_epoch:4.1f}s] Sensor: {reading.sensor_id} | Temp: {reading.temperature_celsius:.1f}°C")
        assert res["tumbling_window_emitted"] is None  # Janela ainda aberta
        assert res["anomaly_detected"] is None

    # -------------------------------------------------------------------------
    # Cenário 2: Roll-over da Janela Tumbling no t = 5.0s
    # -------------------------------------------------------------------------
    print_separator("Cenário 2: Evento no t = 5.0s Força o Fechamento da 1ª Janela Tumbling")
    reading_t5 = SensorReadingEvent("SENSOR-TURBINE-01", 43.0, 5.0)
    res_t5 = pipeline.process_event(reading_t5)

    window_1 = res_t5["tumbling_window_emitted"]
    assert window_1 is not None
    print(f"🎉 Janela Tumbling Finalizada com Sucesso! Intervalo: [{window_1.window_start}s - {window_1.window_end}s)")
    print(f"  Total de Leituras Agregadas: {window_1.reading_count}")
    print(f"  Temperatura Mínima:          {window_1.min_temp:.1f}°C")
    print(f"  Temperatura Máxima:          {window_1.max_temp:.1f}°C")
    print(f"  Temperatura Média:           {window_1.avg_temp:.1f}°C")
    assert window_1.reading_count == 5
    assert window_1.min_temp == 40.5
    assert window_1.max_temp == 42.0
    assert window_1.avg_temp == 41.2

    # -------------------------------------------------------------------------
    # Cenário 3: Detecção de Anomalia de Superaquecimento no t = 8.0s
    # -------------------------------------------------------------------------
    print_separator("Cenário 3: Pico Súbito de Temperatura (94.5°C) no t = 8.0s (Alerta em Tempo Real)")
    pipeline.process_event(SensorReadingEvent("SENSOR-TURBINE-01", 45.0, 6.0))
    pipeline.process_event(SensorReadingEvent("SENSOR-TURBINE-01", 48.0, 7.0))

    # Evento de Pico de Calor Anômalo
    reading_spike = SensorReadingEvent("SENSOR-TURBINE-01", 94.5, 8.0)
    res_spike = pipeline.process_event(reading_spike)

    alert = res_spike["anomaly_detected"]
    assert alert is not None
    print(f"🚨 ALERTA DE STREAMING GERADO!")
    print(f"  Severidade:       {alert.severity}")
    print(f"  Valor Detectado:  {alert.actual_value:.1f}°C (Limiar: {alert.threshold_limit:.1f}°C)")
    print(f"  Motivo:           {alert.reason}")
    assert alert.severity == "CRITICAL"
    assert alert.actual_value == 94.5

    # -------------------------------------------------------------------------
    # Cenário 4: Fechamento da 2ª Janela Tumbling no t = 10.0s
    # -------------------------------------------------------------------------
    print_separator("Cenário 4: Fechamento da 2ª Janela Tumbling [5.0s - 10.0s) com o Pico Histórico")
    pipeline.process_event(SensorReadingEvent("SENSOR-TURBINE-01", 60.0, 9.0))

    # Evento no t = 10.0s fecha a segunda janela
    reading_t10 = SensorReadingEvent("SENSOR-TURBINE-01", 42.0, 10.0)
    res_t10 = pipeline.process_event(reading_t10)
    window_2 = res_t10["tumbling_window_emitted"]
    assert window_2 is not None

    print(f"🎉 2ª Janela Tumbling Finalizada! Intervalo: [{window_2.window_start}s - {window_2.window_end}s)")
    print(f"  Total de Leituras Agregadas: {window_2.reading_count}")
    print(f"  Temperatura Mínima:          {window_2.min_temp:.1f}°C")
    print(f"  Temperatura Máxima (Pico):   {window_2.max_temp:.1f}°C")
    print(f"  Temperatura Média:           {window_2.avg_temp:.1f}°C")
    assert window_2.reading_count == 5
    assert window_2.max_temp == 94.5

    # -------------------------------------------------------------------------
    # Cenário 5: Auditoria Consolidada do Pipeline
    # -------------------------------------------------------------------------
    print_separator("Cenário 5: Métricas e Auditoria do Pipeline de Streaming")
    print(f"Total de Janelas Tumbling Processadas: {len(pipeline.tumbling.completed_windows)}")
    print(f"Total de Alertas Críticos Disparados:  {len(pipeline.sliding.generated_alerts)}")
    assert len(pipeline.tumbling.completed_windows) == 2
    assert len(pipeline.sliding.generated_alerts) == 1

    print_separator("Todos os cenários de Stream Processing e Windowing foram validados com sucesso!")


if __name__ == "__main__":
    main()
