"""Demonstração de Microsserviços: Resiliência com Circuit Breaker e Fallback.

Cenários demonstrados:
1. Circuito FECHADO (CLOSED): Operação normal com personalização por IA
2. Degradação a jusante (Cluster ML instável): Falhas consecutivas abrem o circuito
3. Circuito ABERTO (OPEN - Fail-Fast): Rejeição imediata sem sobrecarregar a rede + Fallback
4. Recuperação Automática (HALF-OPEN -> CLOSED): Restabelecimento do serviço e autocura
5. Telemetria e métricas consolidadas do Circuit Breaker
"""

import sys
import time
from pathlib import Path

# Garante resolução de imports absolutos
sys.path.insert(0, str(Path(__file__).parent))

from resilience.circuit_breaker import CircuitBreaker, CircuitState
from services.ml_scoring_service import MachineLearningScoringService
from services.recommendation_service import RecommendationService


def print_separator(title: str) -> None:
    print(f"\n{'='*75}\n>>> {title}\n{'='*75}")


def main() -> None:
    print("Inicializando Ecossistema com Padrão Circuit Breaker (Hystrix/Resilience)...")

    # Configuração do Circuit Breaker: Abre após 3 falhas, tenta recuperação após 0.2 segundos
    cb = CircuitBreaker(
        name="ml-scoring-breaker",
        failure_threshold=3,
        recovery_timeout_seconds=0.2,
        success_threshold=1,
    )

    ml_service = MachineLearningScoringService()
    recommender = RecommendationService(ml_service, cb)

    # -------------------------------------------------------------------------
    # Cenário 1: Operação Normal (Circuito CLOSED)
    # -------------------------------------------------------------------------
    print_separator("Cenário 1: Operação Normal - IA Saudável (Estado CLOSED)")
    res1 = recommender.get_recommendations_for_user("USER-ALICE")
    print(f"Estado do Circuito: {res1['circuit_state']} | Modo: {res1['mode']}")
    print(f"Recomendações entregues: {[item['title'] for item in res1['recommendations']]}")
    assert cb.state == CircuitState.CLOSED
    assert res1["mode"] == "REALTIME_PERSONALIZED"

    # -------------------------------------------------------------------------
    # Cenário 2: Queda do Serviço Downstream (Disparo do Limiar de Falhas)
    # -------------------------------------------------------------------------
    print_separator("Cenário 2: Falhas Consecutivas no Microsserviço de ML (3 falhas consecutivas)")
    ml_service.set_health(False)

    for i in range(1, 4):
        res = recommender.get_recommendations_for_user(f"USER-FAIL-{i}")
        print(f"Tentativa #{i} | Estado: {res['circuit_state']} | Modo: {res['mode']} | Fallback Ativo: Sim")
        assert res["mode"] == "FALLBACK_DEGRADED"

    # Ao final da 3ª falha consecutiva, o circuito deve estar ABERTO
    assert cb.state == CircuitState.OPEN
    print(f"\n-> Limiar atingido! Circuito transitou para: {cb.state.value}")

    # -------------------------------------------------------------------------
    # Cenário 3: Circuito Aberto (Fail-Fast: Curto-Circuito sem tocar a rede)
    # -------------------------------------------------------------------------
    print_separator("Cenário 3: Circuito OPEN - Rejeição Imediata Fail-Fast (Sem latência de rede)")
    res_open = recommender.get_recommendations_for_user("USER-BOB")
    print(f"Estado do Circuito: {res_open['circuit_state']}")
    print(f"Modo: {res_open['mode']}")
    print(f"Motivo da ativação do Fallback: {res_open['reason']}")
    assert cb.state == CircuitState.OPEN
    assert cb.short_circuited_calls >= 1
    assert res_open["mode"] == "FALLBACK_DEGRADED"

    # -------------------------------------------------------------------------
    # Cenário 4: Autocura e Recuperação (HALF-OPEN -> CLOSED)
    # -------------------------------------------------------------------------
    print_separator("Cenário 4: Recuperação do Serviço Downstream e Autocura do Circuito")
    # Restabelece saúde da IA e aguarda tempo de recuperação
    ml_service.set_health(True)
    print("Aguardando timeout de recuperação (0.2s)...")
    time.sleep(0.25)

    print(f"Estado após timeout (avaliado na próxima chamada): {cb.state.value} (Esperado: HALF_OPEN)")
    assert cb.state == CircuitState.HALF_OPEN

    # Chamada de teste no estado HALF_OPEN
    res_probe = recommender.get_recommendations_for_user("USER-PROBE")
    print(f"Chamada de Sonda executada com sucesso! Modo: {res_probe['mode']}")
    print(f"Novo Estado do Circuito após sucesso: {cb.state.value}")
    assert cb.state == CircuitState.CLOSED
    assert res_probe["mode"] == "REALTIME_PERSONALIZED"

    # -------------------------------------------------------------------------
    # Cenário 5: Métricas de Observabilidade
    # -------------------------------------------------------------------------
    print_separator("Cenário 5: Telemetria Consolidada do Circuit Breaker")
    print(f"Nome do Disjuntor:            {cb.name}")
    print(f"Total de Chamadas Recebidas:  {cb.total_calls}")
    print(f"Chamadas Bem-sucedidas:       {cb.successful_calls}")
    print(f"Chamadas com Falha na Rede:   {cb.failed_calls}")
    print(f"Chamadas em Curto-circuito:   {cb.short_circuited_calls} (Barradas imediatamente no Gateway)")
    print(f"Estado Final Atual:           {cb.state.value}")
    assert cb.short_circuited_calls > 0
    assert cb.state == CircuitState.CLOSED

    print_separator("Todos os cenários do Circuit Breaker foram validados com sucesso!")


if __name__ == "__main__":
    main()
