"""Ponto de Entrada e Demonstração Executável - Exemplo 04: Fintech Digital Wallet.

Demonstra:
1. Módulos com Bounded Contexts em monólito: Accounts, Compliance, Transfers, Notifications.
2. Isolamento de regras regulatórias (PLD / COAF / BACEN) no módulo Compliance sem poluir o módulo de contas.
3. Orquestração atômica de transferência PIX e emissão reativa de notificações.
"""

import sys
import json
from pathlib import Path

# Adiciona diretório do exemplo ao sys.path
sys.path.insert(0, str(Path(__file__).parent))

from shared.events import InProcessEventBus
from modules.accounts import AccountsModule, CreateAccountCommand
from modules.compliance import ComplianceModule
from modules.transfers import TransfersModule, ExecutePixTransferCommand
from modules.notifications import NotificationsModule


def main() -> None:
    print("=" * 80)
    print(" MODULAR MONOLITH - EXEMPLO 04: FINTECH DIGITAL WALLET (PIX & COMPLIANCE)")
    print("=" * 80)

    # 1. Composição de Módulos e Barramento Intra-Processo
    event_bus = InProcessEventBus()

    accounts = AccountsModule()
    compliance = ComplianceModule()
    notifications = NotificationsModule(event_bus=event_bus)
    transfers = TransfersModule(
        accounts_module=accounts,
        compliance_module=compliance,
        event_bus=event_bus,
    )

    # 2. Abertura de Contas Digitais
    print("\n--- 1. Abertura de Contas Digitais (Módulo Accounts) ---")
    carlos = accounts.create_account(CreateAccountCommand(
        owner_name="Carlos Drummond",
        cpf="123.456.789-00",
        pix_key="carlos@drummond.com",
        initial_deposit=5_000.0,
    ))
    clarice = accounts.create_account(CreateAccountCommand(
        owner_name="Clarice Lispector",
        cpf="987.654.321-11",
        pix_key="+552199887766",
        initial_deposit=1_200.0,
    ))
    print(f"Conta Carlos: #{carlos.account_id} | Chave PIX: {carlos.pix_key} | Saldo: R$ {carlos.balance:,.2f}")
    print(f"Conta Clarice: #{clarice.account_id} | Chave PIX: {clarice.pix_key} | Saldo: R$ {clarice.balance:,.2f}")

    # Configura lista de sanções no módulo de Compliance
    compliance.blacklist_pix_key("laranja.fraude@criminoso.com")

    # --------------------------------------------------------------------------
    # CENÁRIO 1: Transferência PIX Válida com Liquidação e Notificação
    # --------------------------------------------------------------------------
    print("\n--- CENÁRIO 1: Transferência PIX Concluída (Carlos -> Clarice: R$ 850,00) ---")
    res_1 = transfers.execute_pix_transfer(ExecutePixTransferCommand(
        origin_account_id=carlos.account_id,
        destination_pix_key="+552199887766",
        amount=850.0,
        description="Pagamento direitos autorais",
    ))
    print(f"Status: {res_1.status} | Código Auth: {res_1.authorization_code} | Msg: {res_1.message}")
    saldo_carlos = accounts.get_account(carlos.account_id).balance
    saldo_clarice = accounts.get_account(clarice.account_id).balance
    print(f"Saldos pós-PIX: Carlos=R$ {saldo_carlos:,.2f} | Clarice=R$ {saldo_clarice:,.2f}")

    # --------------------------------------------------------------------------
    # CENÁRIO 2: Bloqueio Imediato por Blacklist de Compliance
    # --------------------------------------------------------------------------
    print("\n--- CENÁRIO 2: Tentativa de Transferência para Chave em Blacklist (Fraude) ---")
    res_2 = transfers.execute_pix_transfer(ExecutePixTransferCommand(
        origin_account_id=carlos.account_id,
        destination_pix_key="laranja.fraude@criminoso.com",
        amount=500.0,
    ))
    print(f"Status: {res_2.status} | Motivo: {res_2.message}")
    print(f"Saldo de Carlos preservado: R$ {accounts.get_account(carlos.account_id).balance:,.2f}")

    # --------------------------------------------------------------------------
    # CENÁRIO 3: Retenção Regulatória COAF para Alto Valor
    # --------------------------------------------------------------------------
    print("\n--- CENÁRIO 3: Transferência Retida para Quarentena Regulatória COAF (R$ 60.000) ---")
    res_3 = transfers.execute_pix_transfer(ExecutePixTransferCommand(
        origin_account_id=carlos.account_id,
        destination_pix_key="+552199887766",
        amount=60_000.0,
    ))
    print(f"Status: {res_3.status} | Motivo: {res_3.message}")

    # --------------------------------------------------------------------------
    # CENÁRIO 4: Falha por Saldo Insuficiente
    # --------------------------------------------------------------------------
    print("\n--- CENÁRIO 4: Tentativa de Transferência com Saldo Insuficiente ---")
    res_4 = transfers.execute_pix_transfer(ExecutePixTransferCommand(
        origin_account_id=carlos.account_id,
        destination_pix_key="+552199887766",
        amount=4_800.0,  # Carlos possui apenas R$ 4.150
    ))
    print(f"Status: {res_4.status} | Motivo: {res_4.message}")

    # --------------------------------------------------------------------------
    # CENÁRIO 5: Auditoria de Notificações Recebidas pelo Usuário
    # --------------------------------------------------------------------------
    print("\n--- CENÁRIO 5: Notificações Enviadas para Carlos Drummond (Módulo Notifications) ---")
    notifs = notifications.list_notifications(carlos.account_id)
    for idx, n in enumerate(notifs, start=1):
        print(f"  {idx}. [{n.channel}] {n.message}")

    print("\n" + "=" * 80)
    print(" Exemplo 04 de Modular Monolith finalizado com sucesso!")
    print("=" * 80)


if __name__ == "__main__":
    main()
