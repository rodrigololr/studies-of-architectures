"""Demonstração de SOA: Integração de Canais Modernos com Core Bancário Mainframe via ESB.

Cenários demonstrados:
1. Débito doméstico em BRL (sucesso contábil código 00 no mainframe)
2. Débito internacional em USD com mediação e conversão cambial (FX Service)
3. Débito com saldo insuficiente (recusa pelo mainframe código 51)
4. Transação com agência/conta inexistente (recusa código 14)
5. Crédito doméstico em BRL (aumento de saldo contábil)
"""

import sys
from pathlib import Path

# Garante resolução de imports absolutos a partir da raiz do exemplo
sys.path.insert(0, str(Path(__file__).parent))

from mainframe_core.mainframe_ledger import MainframeCobolCore
from services.currency_exchange_service import ForeignExchangeService
from esb.banking_esb import BankingEnterpriseServiceBus


def print_separator(title: str) -> None:
    print(f"\n{'='*75}\n>>> {title}\n{'='*75}")


def main() -> None:
    print("Iniciando barramento SOA bancário com adaptador de mainframe CICS/COBOL...")

    # Inicialização dos participantes da arquitetura SOA
    mainframe = MainframeCobolCore()
    fx_service = ForeignExchangeService()
    esb = BankingEnterpriseServiceBus(mainframe=mainframe, fx_service=fx_service)

    # -------------------------------------------------------------------------
    # Cenário 1: Débito Doméstico BRL (Sucesso)
    # -------------------------------------------------------------------------
    print_separator("Cenário 1: Débito Móvel Doméstico em BRL (Conta 0142 / 0099120)")
    payload_brl = {
        "tx_id": "TXBR000101",
        "branch": "0142",
        "account": "0099120",
        "amount": 250.00,
        "currency": "BRL",
        "type": "D",
    }
    print(f"Payload JSON de entrada (App Mobile):\n  {payload_brl}")
    resp1 = esb.process_mobile_transaction(payload_brl)
    print(f"\nResposta Normalizada do ESB (CDM):\n  Sucesso: {resp1.is_success}")
    print(f"  Código Retorno Mainframe: {resp1.return_code}")
    print(f"  Novo Saldo Contábil: R$ {resp1.new_balance_brl:,.2f}")
    print(f"  Auth Stamp: {resp1.auth_stamp}")
    print(f"  Mensagem: {resp1.message}")
    assert resp1.is_success is True
    assert resp1.return_code == "00"
    assert resp1.new_balance_brl == 4750.00

    # -------------------------------------------------------------------------
    # Cenário 2: Débito Internacional com Mediação de Câmbio (USD -> BRL)
    # -------------------------------------------------------------------------
    print_separator("Cenário 2: Compra Internacional em USD com Mediação FX no ESB")
    payload_usd = {
        "tx_id": "TXUS000202",
        "branch": "0142",
        "account": "0099120",
        "amount": 100.00,
        "currency": "USD",
        "type": "D",
    }
    print(f"Payload JSON de entrada (App Mobile internacional):\n  {payload_usd}")
    resp2 = esb.process_mobile_transaction(payload_usd)
    print(f"\nResposta Normalizada do ESB (CDM):\n  Sucesso: {resp2.is_success}")
    print(f"  Código Retorno Mainframe: {resp2.return_code}")
    print(f"  Novo Saldo Contábil: R$ {resp2.new_balance_brl:,.2f}")
    print(f"  Auth Stamp: {resp2.auth_stamp}")
    print(f"  Mensagem: {resp2.message}")
    assert resp2.is_success is True
    assert resp2.return_code == "00"
    # Taxa USD = 5.40 -> 100 USD = R$ 540.00 -> 4750 - 540 = 4210.00
    assert resp2.new_balance_brl == 4210.00

    # -------------------------------------------------------------------------
    # Cenário 3: Débito com Saldo Insuficiente (Recusa Mainframe Código 51)
    # -------------------------------------------------------------------------
    print_separator("Cenário 3: Débito Superior ao Saldo Disponível (Código 51)")
    payload_insufficient = {
        "tx_id": "TXBR000303",
        "branch": "0142",
        "account": "0099120",
        "amount": 10000.00,
        "currency": "BRL",
        "type": "D",
    }
    print(f"Payload JSON de entrada:\n  {payload_insufficient}")
    resp3 = esb.process_mobile_transaction(payload_insufficient)
    print(f"\nResposta Normalizada do ESB (CDM):\n  Sucesso: {resp3.is_success}")
    print(f"  Código Retorno Mainframe: {resp3.return_code}")
    print(f"  Saldo Inalterado: R$ {resp3.new_balance_brl:,.2f}")
    print(f"  Mensagem: {resp3.message}")
    assert resp3.is_success is False
    assert resp3.return_code == "51"
    assert resp3.new_balance_brl == 4210.00

    # -------------------------------------------------------------------------
    # Cenário 4: Agência e Conta Inexistente (Recusa Mainframe Código 14)
    # -------------------------------------------------------------------------
    print_separator("Cenário 4: Agência/Conta Inexistente no Ledger (Código 14)")
    payload_invalid = {
        "tx_id": "TXBR000404",
        "branch": "9999",
        "account": "0000001",
        "amount": 150.00,
        "currency": "BRL",
        "type": "D",
    }
    print(f"Payload JSON de entrada:\n  {payload_invalid}")
    resp4 = esb.process_mobile_transaction(payload_invalid)
    print(f"\nResposta Normalizada do ESB (CDM):\n  Sucesso: {resp4.is_success}")
    print(f"  Código Retorno Mainframe: {resp4.return_code}")
    print(f"  Mensagem: {resp4.message}")
    assert resp4.is_success is False
    assert resp4.return_code == "14"

    # -------------------------------------------------------------------------
    # Cenário 5: Crédito Doméstico BRL (Sucesso)
    # -------------------------------------------------------------------------
    print_separator("Cenário 5: Depósito / Crédito em Conta (Conta 0142 / 0088340)")
    payload_credit = {
        "tx_id": "TXBR000505",
        "branch": "0142",
        "account": "0088340",
        "amount": 300.00,
        "currency": "BRL",
        "type": "C",
    }
    print(f"Payload JSON de entrada:\n  {payload_credit}")
    resp5 = esb.process_mobile_transaction(payload_credit)
    print(f"\nResposta Normalizada do ESB (CDM):\n  Sucesso: {resp5.is_success}")
    print(f"  Código Retorno Mainframe: {resp5.return_code}")
    print(f"  Novo Saldo Contábil: R$ {resp5.new_balance_brl:,.2f}")
    print(f"  Auth Stamp: {resp5.auth_stamp}")
    print(f"  Mensagem: {resp5.message}")
    assert resp5.is_success is True
    assert resp5.return_code == "00"
    # Saldo original de 0088340 era R$ 1.200,00 -> 1.200 + 300 = 1.500,00
    assert resp5.new_balance_brl == 1500.00

    print_separator("Todos os cenários do Barramento Bancário Mainframe foram validados com sucesso!")


if __name__ == "__main__":
    main()
