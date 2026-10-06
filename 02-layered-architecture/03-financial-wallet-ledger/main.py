"""
main.py - Demonstração executável de Carteira Digital e Ledger em Camadas.

Executa fluxo de abertura de carteira, depósito, saque com saldo suficiente,
bloqueio de saque com saldo insuficiente e visualização do extrato financeiro.
"""

from data.repository import WalletRepository, LedgerRepository
from business.service import WalletService
from presentation.controller import WalletController


def main() -> None:
    print("=" * 65)
    print("DEMONSTRAÇÃO: Carteira Digital e Ledger Financeiro em Camadas")
    print("=" * 65)

    # 1. Composição das camadas
    wallet_repo = WalletRepository()
    ledger_repo = LedgerRepository()
    service = WalletService(wallet_repo, ledger_repo)
    controller = WalletController(service)

    # 2. Abertura de Carteira
    print("\n[PASSO 1] POST /api/wallets (Abertura de Carteira)")
    wallet_res = controller.open_wallet({"user_id": "usr-889"})
    print(f"  HTTP {wallet_res['status_code']}: {wallet_res['data']}")
    wallet_id = wallet_res["data"]["wallet_id"]

    # 3. Depósito de R$ 350.00
    print("\n[PASSO 2] POST /api/wallets/{id}/credit (Depósito inicial)")
    dep_res = controller.deposit(wallet_id, {"amount": 350.0, "description": "PIX Recebido de Cliente"})
    print(f"  HTTP {dep_res['status_code']}: {dep_res['data']}")

    # 4. Saque / Pagamento de R$ 120.00
    print("\n[PASSO 3] POST /api/wallets/{id}/debit (Pagamento de Conta de Luz)")
    saque_res = controller.withdraw(wallet_id, {"amount": 120.0, "description": "Conta de Energia Enel"})
    print(f"  HTTP {saque_res['status_code']}: {saque_res['data']}")

    # 5. Tentativa de saque que excede o saldo (R$ 300.00 com saldo de R$ 230.00)
    print("\n[PASSO 4] POST /api/wallets/{id}/debit (Tentativa de Saque Acima do Saldo)")
    falha_res = controller.withdraw(wallet_id, {"amount": 300.0, "description": "Compra no Cartão"})
    print(f"  HTTP {falha_res['status_code']}: Erro de Negócio = '{falha_res['error']}'")

    # 6. Emissão do Extrato Financeiro
    print("\n[PASSO 5] GET /api/wallets/{id}/statement (Extrato Completo)")
    extrato_res = controller.get_statement(wallet_id)
    extrato = extrato_res["data"]
    print(f"  Saldo Consolidado: R$ {extrato['balance']:.2f}")
    print(f"  Total de Lançamentos no Ledger: {extrato['entries_count']}")
    for e in extrato["history"]:
        sinal = "+" if e["type"] == "CREDIT" else "-"
        print(f"    [{e['timestamp']}] {sinal}R$ {e['amount']:.2f} ({e['description']}) -> Saldo pós: R$ {e['balance_after']:.2f}")

    print("\n" + "=" * 65)


if __name__ == "__main__":
    main()
