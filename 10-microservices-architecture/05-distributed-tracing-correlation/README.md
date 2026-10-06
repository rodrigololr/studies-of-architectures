# 05 - Distributed Tracing & W3C TraceContext (OpenTelemetry / Jaeger Pattern)

Este exemplo demonstra a implementação de **Distributed Tracing (Rastreamento Distribuído)** e propagação de contexto em microsserviços utilizando a especificação formal do **W3C TraceContext** (`traceparent`).

---

## 1. O Desafio Arquitetural

Em sistemas distribuídos:
- Uma única chamada do usuário (ex: "Efetuar Checkout") atravessa múltiplos saltos de rede entre microsserviços:
  $$\text{API Gateway} \longrightarrow \text{Order Service} \longrightarrow \text{Payment Service} \longrightarrow \text{Fraud Detection}$$
- **O Desastre dos Logs Locais Desconectados:** Se uma chamada demorar 3 segundos ou lançar um erro 500 no serviço de fraude, inspecionar logs tradicionais isolados é quase impossível. Cada serviço gera milhares de linhas de log por segundo sem qualquer chave que os correlacione.

---

## 2. Solução via Distributed Tracing & W3C TraceContext

O padrão estabelecido pelo Google Dapper e consolidado no **OpenTelemetry** resolve isso através de um grafo acíclico direcionado (DAG) de **Spans**:

1. **Trace ID (`trace_id`):** Um identificador hexadecimal único de 128 bits gerado na borda (*API Gateway*) que acompanha a requisição por toda a sua jornada distribuída.
2. **Span ID (`span_id`):** Um identificador único de 64 bits para cada operação ou método individual em um microsserviço.
3. **Parent Span ID (`parent_span_id`):** Aponta para o span pai que originou a chamada remota, permitindo montar a árvore hierárquica (*Waterfall View*).
4. **Cabeçalho HTTP W3C `traceparent`:**
   ```
   traceparent: 00-{trace_id}-{span_id}-{flags}
   ```
   Injetado pelo cliente HTTP e extraído pelo servidor HTTP em cada salto da malha de microsserviços.

---

## 3. Diagrama em Cascata (Waterfall Tree)

```mermaid
sequenceDiagram
    autonumber
    actor Cliente as 📱 Mobile Client
    participant GW as 🚪 API Gateway (Root Span)
    participant Order as 📦 Order Service (Child Span)
    participant Pay as 💳 Payment Service (Child Span)
    participant Fraud as 🛡️ Fraud Service (Leaf Span)
    participant Collector as 📊 Telemetry Collector (Jaeger/OTel)

    Cliente->>GW: POST /checkout (Sem headers de rastreamento)
    Note over GW: Cria Trace-ID e Root Span
    GW->>Order: HTTP POST /orders [traceparent: 00-trace_id-gw_span-01]
    Note over Order: Extrai Trace-ID e define parent_span_id = gw_span
    Order->>Pay: HTTP POST /payments [traceparent: 00-trace_id-ord_span-01]
    Note over Pay: Extrai Trace-ID e define parent_span_id = ord_span
    Pay->>Fraud: HTTP POST /fraud-check [traceparent: 00-trace_id-pay_span-01]
    Note over Fraud: Processa e finaliza Span
    
    Fraud-->>Collector: Envia Leaf Span
    Pay-->>Collector: Envia Child Span
    Order-->>Collector: Envia Child Span
    GW-->>Collector: Envia Root Span
    
    Note over Collector: Monta Árvore DAG e Diagnóstico de Causa-Raiz (RCA)
```

---

## 4. Estrutura de Pastas

```
05-distributed-tracing-correlation/
├── tracing/
│   ├── __init__.py
│   ├── trace_context.py       # Manipulação de cabeçalhos W3C traceparent
│   └── tracer.py              # Instrumentação de spans e coletor em memória
├── services/
│   ├── __init__.py
│   ├── api_gateway.py         # Ponto de borda que inicia o Root Span
│   ├── order_service.py       # Microsserviço de Pedidos
│   ├── payment_service.py     # Microsserviço de Pagamentos
│   └── fraud_service.py       # Microsserviço de Detecção de Fraude
├── main.py                    # Cenários de sucesso e Root-Cause Analysis (RCA)
└── README.md
```

---

## 5. Como Executar

```bash
python3 main.py
```
Zero dependências externas necessárias (utiliza apenas Python 3 standard library).
