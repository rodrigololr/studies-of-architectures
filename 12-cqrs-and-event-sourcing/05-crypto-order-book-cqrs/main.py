import sys
from pathlib import Path

# Inclusão do diretório para imports absolutos
sys.path.insert(0, str(Path(__file__).parent))

from infrastructure.event_store import AppendOnlyEventStore
from domain.commands import PlaceLimitOrderCommand, CancelOrderCommand
from application.command_handlers import OrderBookCommandHandler
from projections.l2_depth_chart import L2DepthChartProjection
from projections.market_ticker import MarketTickerProjection

def print_order_book(depth: L2DepthChartProjection, pair: str):
    spread = depth.get_spread()
    mid = depth.get_mid_price()

    print(f"\n--- LIVRO DE OFERTAS L2 ({pair}) ---")
    print(f"Spread: R$ {spread:.2f} | Preço Médio (Mid-Price): R$ {mid:.2f}" if spread else "Sem liquidez bilateral")
    print(f"\n  [ASKS - ORDENS DE VENDA]")
    print(f"  {'Preço (USDT)':>14} | {'Volume (BTC)':>12} | {'Acumulado (BTC)':>15}")
    print("  " + "-" * 47)
    asks = depth.get_asks(limit=5)
    # Exibe asks em ordem decrescente para visualização clássica de trading
    for a in reversed(asks):
        print(f"  {a.price:>14.2f} | {a.volume:>12.4f} | {a.cumulative_volume:>15.4f}")

    print(f"  {' ' * 14} ── SPREAD: ${spread:.2f} ──")

    print(f"\n  [BIDS - ORDENS DE COMPRA]")
    print(f"  {'Preço (USDT)':>14} | {'Volume (BTC)':>12} | {'Acumulado (BTC)':>15}")
    print("  " + "-" * 47)
    bids = depth.get_bids(limit=5)
    for b in bids:
        print(f"  {b.price:>14.2f} | {b.volume:>12.4f} | {b.cumulative_volume:>15.4f}")

def main():
    print("=" * 80)
    print("EXEMPLO 05: CQRS & EVENT SOURCING - LIVRO DE OFERTAS CRIPTO (L2 ORDER BOOK)")
    print("=" * 80)

    event_store = AppendOnlyEventStore()
    depth_projection = L2DepthChartProjection()
    ticker_projection = MarketTickerProjection()

    # Assina as projeções no barramento de eventos
    event_store.subscribe(depth_projection.handle)
    event_store.subscribe(ticker_projection.handle)

    handler = OrderBookCommandHandler(event_store)
    pair = "BTC/USDT"

    print("\n[PASSO 1] Injetando Liquidez Inicial (Makers - Asks de Venda)...")
    handler.handle_place_order(PlaceLimitOrderCommand(pair, "ASK-01", "SELL", 60000.0, 1.0))
    handler.handle_place_order(PlaceLimitOrderCommand(pair, "ASK-02", "SELL", 60100.0, 2.5))
    handler.handle_place_order(PlaceLimitOrderCommand(pair, "ASK-03", "SELL", 60250.0, 5.0))

    print("[PASSO 2] Injetando Liquidez Inicial (Makers - Bids de Compra)...")
    handler.handle_place_order(PlaceLimitOrderCommand(pair, "BID-01", "BUY", 59800.0, 1.2))
    handler.handle_place_order(PlaceLimitOrderCommand(pair, "BID-02", "BUY", 59700.0, 3.0))
    handler.handle_place_order(PlaceLimitOrderCommand(pair, "BID-03", "BUY", 59500.0, 4.0))

    print("\nVisão Inicial das Projeções:")
    print_order_book(depth_projection, pair)

    print("\n" + "=" * 80)
    print("[PASSO 3] EXECUTANDO ORDEM AGRESSIVA DE COMPRA (TAKER ORDER CROSSING)")
    print("=" * 80)
    print(" -> Comprador envia Ordem Limite: COMPRAR 2.0 BTC @ até $60,100.00")
    print("    • Consome 1.0 BTC @ $60,000.00 (Liquidando ASK-01)")
    print("    • Consome 1.0 BTC @ $60,100.00 (Preenchimento parcial de ASK-02 de 2.5 -> 1.5 BTC)")

    handler.handle_place_order(PlaceLimitOrderCommand(pair, "BUY-TAKER-99", "BUY", 60100.0, 2.0))

    print("\n[PASSO 4] CANCELAMENTO DE UMA ORDEM PASSIVA (MAKER CANCEL)")
    print(" -> Comprador da ordem BID-03 ($59,500.00) decide cancelar a ordem.")
    handler.handle_cancel_order(CancelOrderCommand(pair, "BID-03", "MUDANÇA_DE_ESTRATÉGIA"))

    print("\n" + "=" * 80)
    print("ESTADO ATUALIZADO DO LIVRO DE OFERTAS (L2 Depth Chart Projection)")
    print("=" * 80)
    print_order_book(depth_projection, pair)

    print("\n" + "=" * 80)
    print("ESTADO ATUALIZADO DO TICKER 24H (MarketTickerProjection)")
    print("=" * 80)
    ticker = ticker_projection.get_ticker(pair)
    if ticker:
        print(f"Par de Negociação:       {ticker.pair_symbol}")
        print(f"Último Preço Negociado:  $ {ticker.last_price:>12.2f}")
        print(f"Preço Máximo (High):     $ {ticker.high_price:>12.2f}")
        print(f"Preço Mínimo (Low):      $ {ticker.low_price:>12.2f}")
        print(f"Volume Base Total:         {ticker.volume_base:>12.4f} BTC")
        print(f"Volume Financeiro Total: $ {ticker.volume_quote:>12.2f} USDT")
        print(f"Total de Negociações:      {ticker.trades_count:>12} trades")

    print("\n[OK] Motor de Casamento e Projeções CQRS operando perfeitamente.")

if __name__ == "__main__":
    main()
