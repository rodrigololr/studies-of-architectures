import sys
from pathlib import Path

# Adiciona o diretório local ao path para permitir imports absolutos
sys.path.insert(0, str(Path(__file__).parent))

from infrastructure.event_store import AppendOnlyEventStore
from domain.commands import (
    OpenAccountCommand,
    DepositFundsCommand,
    WithdrawFundsCommand,
    TransferFundsCommand,
)
from domain.events import FundsDeposited
from domain.exceptions import InsufficientFundsException, ConcurrencyConflictException
from application.command_handlers import BankAccountCommandHandler
from projections.account_summary import AccountSummaryProjection
from projections.account_statement import AccountStatementProjection

def main():
    print("=" * 80)
    print("EXEMPLO 01: CQRS & EVENT SOURCING - LIVRO-RAZÃO BANCÁRIO COM OCC")
    print("=" * 80)

    # 1. Inicializa o Event Store Append-Only
    event_store = AppendOnlyEventStore()

    # 2. Inicializa as Projeções do Read Side e subscreve aos eventos
    summary_projection = AccountSummaryProjection()
    statement_projection = AccountStatementProjection()

    event_store.subscribe(summary_projection.handle)
    event_store.subscribe(statement_projection.handle)

    # 3. Inicializa o Command Handler do Write Side
    handler = BankAccountCommandHandler(event_store)

    print("\n[CENÁRIO 1] Abertura de Contas")
    alice_id = "ACC-ALICE-001"
    bob_id = "ACC-BOB-002"

    handler.handle_open_account(
        OpenAccountCommand(account_id=alice_id, owner_name="Alice Silva", initial_balance=1000.0)
    )
    print(f" -> Conta '{alice_id}' aberta para Alice com R$ 1.000,00")

    handler.handle_open_account(
        OpenAccountCommand(account_id=bob_id, owner_name="Bob Santos", initial_balance=200.0)
    )
    print(f" -> Conta '{bob_id}' aberta para Bob com R$ 200,00")

    print("\n[CENÁRIO 2] Transações Financeiras (Depósito, Transferência, Saque)")
    handler.handle_deposit(
        DepositFundsCommand(account_id=alice_id, amount=500.0, description="Depósito em Dinheiro")
    )
    print(f" -> Depósito de R$ 500,00 efetuado na conta de Alice.")

    tx_ref = handler.handle_transfer(
        TransferFundsCommand(source_account_id=alice_id, target_account_id=bob_id, amount=300.0)
    )
    print(f" -> Transferência de R$ 300,00 de Alice para Bob (Ref: {tx_ref}) concluída.")

    handler.handle_withdraw(
        WithdrawFundsCommand(account_id=bob_id, amount=150.0, description="Saque Caixa Eletrônico")
    )
    print(f" -> Saque de R$ 150,00 efetuado na conta de Bob.")

    print("\n[CENÁRIO 3] Validação de Invariante de Domínio (Saldo Negativo Rejeitado)")
    try:
        handler.handle_withdraw(
            WithdrawFundsCommand(account_id=bob_id, amount=5000.0, description="Tentativa de Saque Ilícito")
        )
    except InsufficientFundsException as ex:
        print(f" -> [PROTEÇÃO ATIVA] Invariante de negócio disparada com sucesso:")
        print(f"    Erro capturado: {ex}")

    print("\n[CENÁRIO 4] Demonstração de Concorrência Otimista (OCC - Optimistic Concurrency Control)")
    try:
        # Simulamos um processo concorrente que leu a conta na versão 1 e tenta gravar com versão esperada defasada
        stale_version = 1
        stale_event = FundsDeposited(aggregate_id=alice_id, version=stale_version + 1, amount=10.0, description="Concorrente")
        event_store.append_events(
            stream_id=alice_id,
            events=[stale_event],
            expected_version=stale_version,
        )
    except ConcurrencyConflictException as ex:
        print(f" -> [OCC SUCESSO] Conflito concorrente detectado e bloqueado:")
        print(f"    {ex}")

    print("\n[CENÁRIO 5] Consultas no Read Model (Projeções Desnormalizadas)")
    print("-" * 80)
    print("Resumo Geral das Contas (AccountSummaryProjection):")
    for summary in summary_projection.get_all():
        print(f"  • Conta: {summary.account_id} | Titular: {summary.owner_name:<12} | "
              f"Saldo: R$ {summary.balance:>9.2f} | Versão do Stream: {summary.version} | "
              f"Ativa: {summary.is_active}")

    print("\nExtrato Detalhado da Conta de Alice (AccountStatementProjection):")
    print(f"  {'Data/Hora':<26} | {'Operação':<14} | {'Valor (R$)':>12} | {'Saldo Corrente':>14} | {'Descrição'}")
    print("  " + "-" * 105)
    for entry in statement_projection.get_statement(alice_id):
        print(f"  {entry.timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:23]:<26} | "
              f"{entry.operation:<14} | "
              f"{entry.amount:>12.2f} | "
              f"{entry.running_balance:>14.2f} | "
              f"{entry.description}")

    print("\nExtrato Detalhado da Conta de Bob (AccountStatementProjection):")
    print(f"  {'Data/Hora':<26} | {'Operação':<14} | {'Valor (R$)':>12} | {'Saldo Corrente':>14} | {'Descrição'}")
    print("  " + "-" * 105)
    for entry in statement_projection.get_statement(bob_id):
        print(f"  {entry.timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:23]:<26} | "
              f"{entry.operation:<14} | "
              f"{entry.amount:>12.2f} | "
              f"{entry.running_balance:>14.2f} | "
              f"{entry.description}")

    print("\nLog de Auditoria Integral do Event Store (Streams e Versões):")
    for event in event_store.read_all_events():
        print(f"  [v{event.version}] {event.__class__.__name__} -> Stream: {event.aggregate_id} (ID: {event.event_id[:8]})")

    print("\n[OK] Demonstração concluída com sucesso e 100% de integridade garantida.")

if __name__ == "__main__":
    main()
