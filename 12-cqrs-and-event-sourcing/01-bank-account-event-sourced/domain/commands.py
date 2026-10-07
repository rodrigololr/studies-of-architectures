from dataclasses import dataclass

@dataclass(frozen=True)
class Command:
    """Comando base imperativo."""
    pass

@dataclass(frozen=True)
class OpenAccountCommand(Command):
    account_id: str
    owner_name: str
    initial_balance: float = 0.0

@dataclass(frozen=True)
class DepositFundsCommand(Command):
    account_id: str
    amount: float
    description: str = "Depósito"

@dataclass(frozen=True)
class WithdrawFundsCommand(Command):
    account_id: str
    amount: float
    description: str = "Saque"

@dataclass(frozen=True)
class TransferFundsCommand(Command):
    source_account_id: str
    target_account_id: str
    amount: float
    reference_id: str = ""

@dataclass(frozen=True)
class CloseAccountCommand(Command):
    account_id: str
    reason: str = "Encerramento voluntário"
