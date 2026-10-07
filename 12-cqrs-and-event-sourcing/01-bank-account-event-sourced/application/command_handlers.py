from domain.commands import (
    OpenAccountCommand,
    DepositFundsCommand,
    WithdrawFundsCommand,
    TransferFundsCommand,
    CloseAccountCommand,
)
from domain.aggregate import BankAccountAggregate
from infrastructure.event_store import AppendOnlyEventStore
import uuid

class BankAccountCommandHandler:
    """
    Orquestrador do Write Side:
    1. Carrega o stream de eventos a partir do Event Store.
    2. Re-hidrata a instância do Agregado.
    3. Executa a operação de negócio para validar invariantes.
    4. Grava os novos eventos no Event Store sob Controle de Concorrência Otimista (OCC).
    """

    def __init__(self, event_store: AppendOnlyEventStore):
        self._event_store = event_store

    def handle_open_account(self, cmd: OpenAccountCommand) -> None:
        stream = self._event_store.read_stream(cmd.account_id)
        expected_version = len(stream)

        aggregate = BankAccountAggregate(cmd.account_id)
        aggregate.rehydrate(stream)
        aggregate.open(owner_name=cmd.owner_name, initial_balance=cmd.initial_balance)

        self._event_store.append_events(
            stream_id=cmd.account_id,
            events=aggregate.uncommitted_events,
            expected_version=expected_version,
        )
        aggregate.clear_uncommitted_events()

    def handle_deposit(self, cmd: DepositFundsCommand) -> None:
        stream = self._event_store.read_stream(cmd.account_id)
        expected_version = len(stream)

        aggregate = BankAccountAggregate(cmd.account_id)
        aggregate.rehydrate(stream)
        aggregate.deposit(amount=cmd.amount, description=cmd.description)

        self._event_store.append_events(
            stream_id=cmd.account_id,
            events=aggregate.uncommitted_events,
            expected_version=expected_version,
        )
        aggregate.clear_uncommitted_events()

    def handle_withdraw(self, cmd: WithdrawFundsCommand) -> None:
        stream = self._event_store.read_stream(cmd.account_id)
        expected_version = len(stream)

        aggregate = BankAccountAggregate(cmd.account_id)
        aggregate.rehydrate(stream)
        aggregate.withdraw(amount=cmd.amount, description=cmd.description)

        self._event_store.append_events(
            stream_id=cmd.account_id,
            events=aggregate.uncommitted_events,
            expected_version=expected_version,
        )
        aggregate.clear_uncommitted_events()

    def handle_transfer(self, cmd: TransferFundsCommand) -> str:
        ref_id = cmd.reference_id or f"TX-{uuid.uuid4().hex[:8].upper()}"

        # 1. Débito na conta de origem
        source_stream = self._event_store.read_stream(cmd.source_account_id)
        source_expected_version = len(source_stream)
        source_agg = BankAccountAggregate(cmd.source_account_id)
        source_agg.rehydrate(source_stream)
        source_agg.transfer_out(target_account_id=cmd.target_account_id, amount=cmd.amount, reference_id=ref_id)

        self._event_store.append_events(
            stream_id=cmd.source_account_id,
            events=source_agg.uncommitted_events,
            expected_version=source_expected_version,
        )
        source_agg.clear_uncommitted_events()

        # 2. Crédito na conta de destino
        target_stream = self._event_store.read_stream(cmd.target_account_id)
        target_expected_version = len(target_stream)
        target_agg = BankAccountAggregate(cmd.target_account_id)
        target_agg.rehydrate(target_stream)
        target_agg.transfer_in(source_account_id=cmd.source_account_id, amount=cmd.amount, reference_id=ref_id)

        self._event_store.append_events(
            stream_id=cmd.target_account_id,
            events=target_agg.uncommitted_events,
            expected_version=target_expected_version,
        )
        target_agg.clear_uncommitted_events()

        return ref_id

    def handle_close_account(self, cmd: CloseAccountCommand) -> None:
        stream = self._event_store.read_stream(cmd.account_id)
        expected_version = len(stream)

        aggregate = BankAccountAggregate(cmd.account_id)
        aggregate.rehydrate(stream)
        aggregate.close(reason=cmd.reason)

        self._event_store.append_events(
            stream_id=cmd.account_id,
            events=aggregate.uncommitted_events,
            expected_version=expected_version,
        )
        aggregate.clear_uncommitted_events()
