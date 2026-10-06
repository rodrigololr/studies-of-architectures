# 06 - Stream Processing & Time Windowing (Janelas Temporais e Detecção de Anomalias)

Este exemplo demonstra a implementação dos conceitos fundamentais de **Stream Processing (Processamento de Fluxos Contínuos)** em Event-Driven Architecture (padrão consagrado em *Apache Flink*, *Kafka Streams* e *Spark Streaming*), utilizando **Janelas de Salto (*Tumbling Windows*)** e **Janelas Deslizantes (*Sliding Windows*)** para telemetria IoT e detecção de anomalias em tempo real.

---

## 1. O Desafio Arquitetural

Em sistemas modernos de Internet das Coisas (IoT), telemetria veicular, mercado financeiro e monitoramento de infraestrutura, os dados não chegam como tabelas estáticas, mas como um **fluxo infinito e ininterrupto de eventos ao longo do tempo**:
- Como calcular a temperatura média de uma turbina sem armazenar gigabytes de histórico bruto?
- Como detectar um pico súbito de calor ou uma fraude financeira em menos de 100ms antes que cause danos físicos?

---

## 2. Solução via Operadores de Janelas Temporais

O processamento de streams resolve isso particionando o fluxo temporal contínuo em **janelas discretas**:

### 1. Janela de Salto / Fixa (*Tumbling Window*)
- Intervalos de tempo de tamanho fixo, contíguos e **não sobrepostos** (ex: $[0s - 5s)$, $[5s - 10s)$, $[10s - 15s)$).
- Cada evento pertence a exatamente uma única janela.
- Quando o relógio avança além do limite final da janela, ela fecha automaticamente e emite um evento sumarizado com agregações consolidadas (mínimo, máximo, contagem, média).

### 2. Janela Deslizante (*Sliding Window*)
- Mantém um buffer contínuo dos eventos que ocorreram nos últimos $N$ segundos em relação ao instante atual.
- Conforme novos eventos chegam, os eventos que ultrapassaram a cauda da janela são expulsos (*eviction*).
- Ideal para **Detecção de Anomalias e Picos**: se qualquer leitura dentro da janela ultrapassar o limiar crítico ($85^\circ\text{C}$), um evento de alerta de severidade crítica é disparado imediatamente em tempo real.

---

## 3. Diagrama Comparativo de Janelas Temporais (Mermaid)

```mermaid
flowchart TD
    subgraph Stream["Fluxo Contínuo de Eventos (Event Stream)"]
        E1["t=0s: 40.5°C"] --> E2["t=1s: 41.2°C"] --> E3["t=2s: 42.0°C"] --> E4["t=5s: 43.0°C"] --> E5["t=8s: 94.5°C (PICO)"]
    end

    subgraph Tumbling["Janela de Salto (Tumbling Window - 5s)"]
        W1["Janela 1: [0.0s - 5.0s)<br/>Média: 41.2°C | Máx: 42.0°C"]
        W2["Janela 2: [5.0s - 10.0s)<br/>Média: 58.1°C | Máx: 94.5°C"]
    end

    subgraph Sliding["Janela Deslizante (Sliding Window - Anomalias)"]
        Alert["🚨 AnomalyAlertEvent<br/>Superaquecimento detectado: 94.5°C<br/>no t=8.0s (CRITICAL)"]
    end

    Stream -->|Agregação Discreta| Tumbling
    E5 -->|Inspeção Imediata| Alert

    classDef default fill:#f8fafc,stroke:#334155,stroke-width:1px,color:#0f172a;
    classDef alert fill:#fee2e2,stroke:#b91c1c,stroke-width:2px,color:#7f1d1d;
    classDef window fill:#dbeafe,stroke:#1d4ed8,stroke-width:1px,color:#1e3a8a;
    class Alert alert;
    class W1,W2 window;
```

---

## 4. Estrutura de Pastas

```
06-stream-processing-windowing/
├── stream/
│   ├── __init__.py
│   ├── telemetry_events.py    # Eventos de leitura, sumário de janela e alerta
│   ├── tumbling_window.py     # Agregador de janelas fixas não sobrepostas
│   └── sliding_window.py      # Detector de anomalias com janela contínua móvel
├── pipeline/
│   ├── __init__.py
│   └── stream_processor.py    # Coordenador do pipeline de streaming
├── main.py                    # Cenários de teste executáveis
└── README.md
```

---

## 5. Como Executar

```bash
python3 main.py
```
Zero dependências externas necessárias (utiliza apenas Python 3 standard library).
