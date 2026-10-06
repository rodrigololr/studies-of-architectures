"""
main.py - Composition Root e Demonstração do Exemplo 05.
"""

import sys
import json
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.service import CryptoOracleAggregatorService
from adapters.secondary.binance_adapter import BinanceExchangeAdapter
from adapters.secondary.coingecko_adapter import CoinGeckoAdapter
from adapters.secondary.kraken_adapter import KrakenExchangeAdapter
from adapters.secondary.in_memory_price_cache_adapter import InMemoryPriceCacheAdapter
from adapters.secondary.in_memory_oracle_audit_adapter import InMemoryOracleAuditAdapter
from adapters.primary.rest_exchange_rate_controller import RestExchangeRateController
from adapters.primary.websocket_ticker_adapter import WebsocketTickerSubscriptionAdapter


def main() -> None:
    print("=" * 80)
    print(" HEXAGONAL ARCHITECTURE - EXEMPLO 05: CRYPTO CURRENCY EXCHANGE RATES (ORACLE)")
    print("=" * 80)

    # 1. Adaptadores Secundários (Driven)
    binance = BinanceExchangeAdapter({
        "BTC-USD": 68250.00,
        "ETH-USD": 3520.00,
        "SOL-USD": 182.50,
    })
    coingecko = CoinGeckoAdapter({
        "BTC-USD": 68290.00,
        "ETH-USD": 3515.00,
        "SOL-USD": 183.10,
    })
    kraken = KrakenExchangeAdapter({
        "BTC-USD": 68270.00,
        "ETH-USD": 3525.00,
        "SOL-USD": 182.90,
    })
    cache = InMemoryPriceCacheAdapter()
    audit_repo = InMemoryOracleAuditAdapter()

    # 2. Núcleo da Aplicação (Core / Hexágono)
    oracle_service = CryptoOracleAggregatorService(
        providers=[binance, coingecko, kraken],
        cache=cache,
        audit_repo=audit_repo,
        cache_ttl_seconds=3,
        min_quorum=2,
    )

    # 3. Adaptadores Primários (Driver)
    rest_controller = RestExchangeRateController(use_case=oracle_service)
    ws_adapter = WebsocketTickerSubscriptionAdapter(use_case=oracle_service)

    print("\n--- CENÁRIO 1: Consulta Inicial Agregada (Live Quorum de 3 Fontes) ---")
    status, res = rest_controller.handle_get_rate("BTC-USD")
    print(f"Status HTTP: {status}")
    print(json.dumps(res, indent=2, ensure_ascii=False))

    print("\n--- CENÁRIO 2: Segunda Consulta Imediata -> Cache Hit (Sem onerar as APIs) ---")
    status, res = rest_controller.handle_get_rate("BTC-USD")
    print(f"Status HTTP: {status} | Cache Hit: {res['data']['cached']} | Preço: $ {res['data']['median_price_usd']:,.2f}")

    print("\n--- CENÁRIO 3: Resistência a Outlier / Glitch Anômalo (Spike de Preço) ---")
    cache.clear()  # Força nova consulta
    # Binance tem anomalia/glitch de ordem e reporta $98.000,00 temporariamente
    binance.set_price("BTC-USD", 98000.00)
    print("[Simulação] Provedor Binance reportando pico falso de $ 98,000.00.")

    status, res = rest_controller.handle_get_rate("BTC-USD")
    print(f"Status HTTP: {status}")
    print(f"Preço Mediano Apurado: $ {res['data']['median_price_usd']:,.2f}")
    print(f"Observação: A mediana descartou o efeito do outlier da Binance ({res['data']['sources']})!")

    # Restaura preço normal
    binance.set_price("BTC-USD", 68250.00)

    print("\n--- CENÁRIO 4: Falha de Quórum Mínimo (2 de 3 exchanges indisponíveis) ---")
    cache.clear()
    binance.set_online(False)
    kraken.set_online(False)
    print("[Simulação] Binance e Kraken caíram simultaneamente.")

    status, res = rest_controller.handle_get_rate("BTC-USD")
    print(f"Status HTTP: {status} | Resposta: {res}")

    # Restaura
    binance.set_online(True)
    kraken.set_online(True)

    print("\n--- CENÁRIO 5: Acionamento via Adaptador WebSocket Streaming ---")
    cache.clear()
    ws_tick = ws_adapter.broadcast_tick("SOL-USD")
    print(ws_tick)

    print("\n--- CENÁRIO 6: Rejeição de Símbolo Não Homologado ---")
    status, res = rest_controller.handle_get_rate("DOGE-USDT")
    print(f"Status HTTP: {status} | Resposta: {res}")

    print("\n--- CENÁRIO 7: Auditoria Gravada no Repositório Secundário ---")
    history = audit_repo.list_history()
    print(f"Total de cotações arquivadas pelo oráculo: {len(history)}")
    for rate in history:
        print(f" -> [{rate.calculated_at.strftime('%H:%M:%S')}] {rate.symbol}: $ {rate.median_price:,.2f} ({len(rate.sources_used)} fontes, spread: {rate.spread_percentage:.2f}%)")

    print("\n" + "=" * 80)
    print(" Exemplo 05 finalizado com sucesso!")
    print("=" * 80)


if __name__ == "__main__":
    main()
