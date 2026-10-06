"""Demonstração de Microsserviços: Service Discovery & Client-Side Load Balancing.

Cenários demonstrados:
1. Registro dinâmico de instâncias no Service Registry (Netflix Eureka / Consul)
2. Balanceamento Round-Robin no lado do cliente (Netflix Ribbon)
3. Elasticidade e Scale-Up em tempo real (Adição da 4ª instância no pool)
4. Falha de Heartbeat e Evicção de instâncias mortas no Registry
5. Rebalanceamento transparente sem interrupção de serviço
"""

import sys
import time
from collections import Counter
from pathlib import Path

# Garante resolução de imports absolutos
sys.path.insert(0, str(Path(__file__).parent))

from discovery.service_instance import ServiceInstance, InstanceStatus
from discovery.service_registry import ServiceRegistry
from discovery.load_balancer import RoundRobinLoadBalancer
from client.order_service_client import OrderServiceClient


def print_separator(title: str) -> None:
    print(f"\n{'='*75}\n>>> {title}\n{'='*75}")


def main() -> None:
    print("Inicializando Service Registry e Balanceador Client-Side...")

    # 1. Inicializa o Registro de Serviços (Eureka simulator) com TTL de 0.2s
    registry = ServiceRegistry(default_ttl_seconds=0.2)

    # -------------------------------------------------------------------------
    # Cenário 1: Inicialização e Registro de 3 Instâncias do PaymentService
    # -------------------------------------------------------------------------
    print_separator("Cenário 1: Registro Inicial de 3 Instâncias do PaymentService")
    inst1 = ServiceInstance("pay-inst-01", "PAYMENT-SERVICE", "10.0.1.10", 8081)
    inst2 = ServiceInstance("pay-inst-02", "PAYMENT-SERVICE", "10.0.1.11", 8082)
    inst3 = ServiceInstance("pay-inst-03", "PAYMENT-SERVICE", "10.0.1.12", 8083)

    registry.register(inst1)
    registry.register(inst2)
    registry.register(inst3)

    active_instances = registry.get_healthy_instances("PAYMENT-SERVICE")
    print(f"Total de instâncias ativas no Registry: {len(active_instances)}")
    for inst in active_instances:
        print(f"  - [{inst.instance_id}] URL: {inst.endpoint_url} (Status: {inst.status.value})")
    assert len(active_instances) == 3

    # -------------------------------------------------------------------------
    # Cenário 2: Balanceamento Round-Robin no Cliente (6 Requisições)
    # -------------------------------------------------------------------------
    print_separator("Cenário 2: Execução de 6 Requisições com Balanceamento Round-Robin")
    balancer = RoundRobinLoadBalancer(registry, "PAYMENT-SERVICE")
    client = OrderServiceClient(balancer)

    served_by_list = []
    for i in range(1, 7):
        res = client.invoke_payment_service(f"ORD-{1000 + i}", 150.0 * i)
        served_by_list.append(res["served_by_instance"])
        print(f"Requisição #{i} -> Atendida por: {res['served_by_instance']} ({res['endpoint_target']})")

    # Verifica se cada uma das 3 instâncias atendeu exatamente 2 chamadas
    counts = Counter(served_by_list)
    print(f"\nDistribuição de Carga: {dict(counts)}")
    assert counts["pay-inst-01"] == 2
    assert counts["pay-inst-02"] == 2
    assert counts["pay-inst-03"] == 2

    # -------------------------------------------------------------------------
    # Cenário 3: Scale-Up Elástico (Entrada da 4ª Instância)
    # -------------------------------------------------------------------------
    print_separator("Cenário 3: Scale-Up Dinâmico - Adicionando 'pay-inst-04'")
    inst4 = ServiceInstance("pay-inst-04", "PAYMENT-SERVICE", "10.0.1.13", 8084)
    registry.register(inst4)

    active_now = registry.get_healthy_instances("PAYMENT-SERVICE")
    print(f"Novo total de instâncias registradas: {len(active_now)}")
    assert len(active_now) == 4

    # Dispara 4 novas requisições: todas as 4 instâncias devem ser visitadas no ciclo
    cycle_4 = [client.invoke_payment_service(f"ORD-{i}", 50.0)["served_by_instance"] for i in range(2001, 2005)]
    print(f"Próximas 4 requisições atendidas por: {cycle_4}")
    assert set(cycle_4) == {"pay-inst-01", "pay-inst-02", "pay-inst-03", "pay-inst-04"}

    # -------------------------------------------------------------------------
    # Cenário 4: Queda de Instância e Evicção por Falta de Heartbeat
    # -------------------------------------------------------------------------
    print_separator("Cenário 4: Queda da Instância 'pay-inst-02' e Expulsão (Eviction)")
    # Renovamos heartbeat de 01, 03 e 04, deixando 02 expirar propositalmente
    print("Aguardando expiração de heartbeat da instância 02 (0.25s)...")
    time.sleep(0.25)
    registry.heartbeat("PAYMENT-SERVICE", "pay-inst-01")
    registry.heartbeat("PAYMENT-SERVICE", "pay-inst-03")
    registry.heartbeat("PAYMENT-SERVICE", "pay-inst-04")

    evicted = registry.evict_dead_instances(ttl_seconds=0.2)
    print(f"Instâncias expulsas pelo Registry por timeout de heartbeat: {evicted}")
    assert "pay-inst-02" in evicted
    remaining = registry.get_healthy_instances("PAYMENT-SERVICE")
    print(f"Instâncias remanescentes saudáveis: {[i.instance_id for i in remaining]}")
    assert len(remaining) == 3

    # -------------------------------------------------------------------------
    # Cenário 5: Rebalanceamento Transparente Pós-Evicção
    # -------------------------------------------------------------------------
    print_separator("Cenário 5: Rebalanceamento Contínuo sem a Instância 02")
    post_eviction_targets = [
        client.invoke_payment_service(f"ORD-{i}", 100.0)["served_by_instance"]
        for i in range(3001, 3007)
    ]
    print(f"6 requisições pós-evicção atendidas por: {post_eviction_targets}")
    assert "pay-inst-02" not in post_eviction_targets
    assert set(post_eviction_targets) == {"pay-inst-01", "pay-inst-03", "pay-inst-04"}

    print_separator("Todos os cenários de Service Discovery e Load Balancing foram validados com sucesso!")


if __name__ == "__main__":
    main()
