from typing import List, Optional
from domain.events import (
    DomainEvent,
    AccountOpened,
    FundsDeposited,
    FundsWithdrawn,
    FundsTransferredOut,
    FundsTransferredIn,
    AccountClosed,
)
from domain.exceptions import (
    AccountInactiveException,
    InsufficientFundsException,
    InvalidAmountException,
    AccountAlreadyExistsException,
)

class BankAccountAggregate:
    """
    Agregado de Conta Bancária (Aggregate Root).
    Não realiza operações de I/O.
    Seu estado interno é construído exclusivamente através da re-hidratação de eventos passados.
    """

    def __init__(self, account_id: str):
        self.account_id: str = account_id
        self.owner_name: str = ""
        self.balance: float = 0.0
        self.is_active: bool = False
        self.is_closed: bool = False
        self.version: int = 0
        self._uncommitted_events: List[DomainEvent] = []

    @property
    def uncommitted_events(self) -> List[DomainEvent]:
        return list(self._uncommitted_events)

    def clear_uncommitted_events(self) -> None:
        self._uncommitted_events.clear()

    # =========================================================================
    # RE-HIDRATAÇÃO (Replaying de Eventos)
    # =========================================================================

    def rehydrate(self, events: List[DomainEvent]) -> None:
        """Reconstrói o estado acumulado aplicando a sequência histórica de eventos."""
        for event in events:
            self._apply(event)
            self.version = event.version
        self._uncommitted_events.clear()

    def _record_that(self, event: DomainEvent) -> None:
        """Aplica a mutação de estado localmente e enfileira o evento para persistência."""
        self._apply(event)
        self._uncommitted_events.append(event)

    def _apply(self, event: DomainEvent) -> None:
        """
        Método despachante de mutação pura de estado.
        NUNCA deve gerar efeitos colaterais (HTTP, IO, novos GUIDs, datas do sistema).
        """
        if isinstance(event, AccountOpened):
            self.owner_name = event.owner_name
            self.balance = event.initial_balance
            self.is_active = True
            self.is_closed = False
        elif isinstance(event, FundsDeposited):
            self.balance += event.amount
        elif isinstance(event, FundsWithdrawn):
            self.balance -= event.amount
        elif isinstance(event, FundsTransferredOut):
            self.balance -= event.amount
        elif isinstance(event, FundsTransferredIn):
            self.balance += event.amount
        elif isinstance(event, AccountClosed):
            self.is_active = False
            self.is_closed = True

    # =========================================================================
    # OPERAÇÕES DE NEGÓCIO (Comandos de Domínio & Validação de Invariantes)
    # =========================================================================

    def open(self, owner_name: str, initial_balance: float = 0.0) -> None:
        if self.is_active or self.is_closed:
            raise AccountAlreadyExistsException(f"Conta '{self.account_id}' já foi inicializada.")
        if not owner_name or not owner_name.strip():
            raise ValueError("Nome do titular não pode ser vazio.")
        if initial_balance < 0:
            raise InvalidAmountException("Saldo inicial não pode ser negativo.")

        next_version = self.version + len(self._uncommitted_events) + 1
        self._record_that(
            AccountOpened(
                aggregate_id=self.account_id,
                version=next_version,
                owner_name=owner_name.strip(),
                initial_balance=initial_balance,
            )
        )

    def deposit(self, amount: float, description: str = "Depósito") -> None:
        self._assert_account_is_operable()
        if amount <= 0:
            raise InvalidAmountException(f"O valor de depósito deve ser positivo. Recebido: {amount}")

        next_version = self.version + len(self._uncommitted_events) + 1
        self._record_that(
            FundsDeposited(
                aggregate_id=self.account_id,
                version=next_version,
                amount=amount,
                description=description,
            )
        )

    def withdraw(self, amount: float, description: str = "Saque") -> None:
        self._assert_account_is_operable()
        if amount <= 0:
            raise InvalidAmountException(f"O valor de saque deve ser positivo. Recebido: {amount}")
        if self.balance < amount:
            raise InsufficientFundsException(
                f"Saldo insuficiente na conta '{self.account_id}'. "
                f"Disponível: R$ {self.balance:.2f}, Solicitado: R$ {amount:.2f}"
            )

        next_version = self.version + len(self._uncommitted_events) + 1
        self._record_that(
            FundsWithdrawn(
                aggregate_id=self.account_id,
                version=next_version,
                amount=amount,
                description=description,
            )
        )

    def transfer_out(self, target_account_id: str, amount: float, reference_id: str) -> None:
        self._assert_account_is_operable()
        if amount <= 0:
            raise InvalidAmountException(f"O valor da transferência deve ser positivo. Recebido: {amount}")
        if self.balance < amount:
            raise InsufficientFundsException(
                f"Saldo insuficiente para transferir da conta '{self.account_id}'. "
                f"Disponível: R$ {self.balance:.2f}, Solicitado: R$ {amount:.2f}"
            )

        next_version = self.version + len(self._uncommitted_events) + 1
        self._record_that(
            FundsTransferredOut(
                aggregate_id=self.account_id,
                version=next_version,
                amount=amount,
                target_account_id=target_account_id,
                reference_id=reference_id,
            )
        )

    def transfer_in(self, source_account_id: str, amount: float, reference_id: str) -> None:
        self._assert_account_is_operable()
        if amount <= 0:
            raise InvalidAmountException(f"O valor de recebimento deve ser positivo. Recebido: {amount}")

        next_version = self.version + len(self._uncommitted_events) + 1
        self._record_that(
            FundsTransferredIn(
                aggregate_id=self.account_id,
                version=next_version,
                amount=amount,
                source_account_id=source_account_id,
                reference_id=reference_id,
            )
        )

    def close(self, reason: str = "Encerramento voluntário") -> None:
        self._assert_account_is_operable()
        if self.balance != 0:
            raise DomainException(
                f"Não é possível encerrar conta com saldo diferente de zero. "
                f"Saldo remanescente: R$ {self.balance:.2f}"
            )

        next_version = self.version + len(self._uncommitted_events) + 1
        self._record_that(
            AccountClosed(
                aggregate_id=self.account_id,
                version=next_version,
                reason=reason,
            )
        )

    def _assert_account_is_operable(self) -> None:
        if not self.is_active:
            raise AccountInactiveException(f"Conta '{self.account_id}' não está ativa.")
        if self.is_closed:
            raise AccountInactiveException(f"Conta '{self.account_id}' está permanentemente encerrada.")
