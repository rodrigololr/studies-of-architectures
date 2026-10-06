"""Demonstração de Microsserviços: Distributed Tracing com W3C TraceContext.

Cenários demonstrados:
1. Transação Distribuída de Sucesso:
   - Propagação de Trace-ID e Parent-Span-ID através de 4 microsserviços
   - Gateway -> OrderService -> PaymentService -> FraudDetectionService
   - Exibição da Árvore de Rastreamento (Waterfall DAG) com durações em milissegundos
2. Transação Rejeitada com Falha em Profundidade:
   - Identificação precisa da causa-raiz do erro (RCA) no serviço folha da cadeia
   - Marcação de status de erro e atributos em toda a pilha do trace
"""

import sys
from pathlib import Path

# Garante resolução de imports absolutos
sys.path.insert(0, str(Path(__file__).parent))

from tracing.tracer import Tracer, InMemorySpanCollector
from services.fraud_service import FraudDetectionService
from services.payment_service import PaymentService
from services.order_service import OrderService
from services.api_gateway import ApiGatewayService


def print_separator(title: str) -> None:
    print(f"\n{'='*75}\n>>> {title}\n{'='*75}")


def print_trace_waterfall(collector: InMemorySpanCollector, trace_id: str) -> None:
    spans = collector.get_trace_tree(trace_id)
    print(f"\nVisualizador de Rastreamento Distribuído (Trace-ID: {trace_id})")
    print("-" * 75)

    # Cria mapa de níveis de profundidade
    depths = {}
    for span in spans:
        if span.parent_span_id is None:
            depths[span.span_id] = 0
        else:
            depths[span.span_id] = depths.get(span.parent_span_id, 0) + 1

    for span in spans:
        indent = "    " * depths.get(span.span_id, 0)
        status_badge = "[OK]" if span.status == "OK" else "[ERROR]"
        print(
            f"{indent}↳ {status_badge} [{span.service_name:<16}] {span.name:<26} "
            f"| Dur: {span.duration_ms:5.1f}ms | Span: {span.span_id[:8]}"
        )
        if span.error_message:
            print(f"{indent}    ⚠️  Causa do Erro: {span.error_message}")


def main() -> None:
    print("Inicializando Ecossistema de Microsserviços com Telemetria e Distributed Tracing...")

    # 1. Coletor Centralizado de Spans (estilo Jaeger / OpenTelemetry Collector)
    collector = InMemorySpanCollector()

    # 2. Inicialização dos Tracers por Microsserviço
    gw_tracer = Tracer("api-gateway", collector)
    order_tracer = Tracer("order-service", collector)
    pay_tracer = Tracer("payment-service", collector)
    fraud_tracer = Tracer("fraud-service", collector)

    # 3. Inicialização dos Serviços Encadeados
    fraud_svc = FraudDetectionService(fraud_tracer)
    pay_svc = PaymentService(pay_tracer, fraud_svc)
    order_svc = OrderService(order_tracer, pay_svc)
    gateway_svc = ApiGatewayService(gw_tracer, order_svc)

    # -------------------------------------------------------------------------
    # Cenário 1: Checkout de Sucesso (R$ 450,00)
    # -------------------------------------------------------------------------
    print_separator("Cenário 1: Transação Bem-Sucedida de Checkout através de 4 Saltos de Rede")
    order_res, trace_id_1 = gateway_svc.handle_checkout_request(
        order_id="ORD-SUCCESS-101", customer_id="CUST-ALICE", amount=450.00
    )
    print(f"Pedido Concluído: {order_res['order_id']} | Status: {order_res['order_status']}")
    print_trace_waterfall(collector, trace_id_1)

    spans_1 = collector.get_trace_tree(trace_id_1)
    assert len(spans_1) == 4
    # Todos devem compartilhar rigorosamente o mesmo trace_id
    assert all(s.trace_id == trace_id_1 for s in spans_1)
    # Todos com status OK
    assert all(s.status == "OK" for s in spans_1)
    # Verifica a cadeia hierárquica de spans
    gw_span = next(s for s in spans_1 if s.service_name == "api-gateway")
    ord_span = next(s for s in spans_1 if s.service_name == "order-service")
    pay_span = next(s for s in spans_1 if s.service_name == "payment-service")
    fraud_span = next(s for s in spans_1 if s.service_name == "fraud-service")
    assert gw_span.parent_span_id is None
    assert ord_span.parent_span_id == gw_span.span_id
    assert pay_span.parent_span_id == ord_span.span_id
    assert fraud_span.parent_span_id == pay_span.span_id

    # -------------------------------------------------------------------------
    # Cenário 2: Transação Bloqueada por Suspeita de Fraude (R$ 25.000,00)
    # -------------------------------------------------------------------------
    print_separator("Cenário 2: Transação Bloqueada por Fraude com Diagnóstico de Causa-Raiz (RCA)")
    trace_id_2 = None
    try:
        _, trace_id_2 = gateway_svc.handle_checkout_request(
            order_id="ORD-FRAUD-999", customer_id="CUST-UNKNOWN", amount=25000.00
        )
    except ValueError as exc:
        print(f"Exceção capturada na borda: {exc}")

    # Localiza o trace do pedido fraudulento
    all_spans = collector._spans
    fraud_spans = [s for s in all_spans if s.attributes.get("order.id") == "ORD-FRAUD-999" or s.attributes.get("transaction.amount") == 25000.00]
    trace_id_2 = fraud_spans[0].trace_id

    print_trace_waterfall(collector, trace_id_2)

    spans_2 = collector.get_trace_tree(trace_id_2)
    assert len(spans_2) == 4
    # Todos os spans da chamada falha devem conter status ERROR
    assert all(s.status == "ERROR" for s in spans_2)
    # A causa raiz deve estar registrada no serviço de fraude
    fraud_span_error = next(s for s in spans_2 if s.service_name == "fraud-service")
    assert "ALERTA DE FRAUDE" in fraud_span_error.error_message

    print_separator("Todos os cenários de Distributed Tracing foram validados com sucesso!")


if __name__ == "__main__":
    main()
