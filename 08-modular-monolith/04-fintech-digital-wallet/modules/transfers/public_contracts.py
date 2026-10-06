"""Contrato Público do Módulo Transfers (Orquestrador PIX)."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from shared.events import DomainEvent


@dataclass(frozen=True)
class ExecutePixTransferCommand:
    origin_account_id: str
    destination_pix_key: str
    amount: float
    description: str = "Transferência Instantânea PIX"


@dataclass(frozen=True)
class TransferResultDto:
    transfer_id: str
    origin_account_id: str
    destination_pix_key: str
    amount: float
    status: str  # "COMPLETED", "REJECTED_COMPLIANCE", "FAILED_INSUFFICIENT_FUNDS", "DESTINATION_NOT_FOUND"
    authorization_code: Optional[str]
    message: str


@dataclass(frozen=True)
class TransferCompletedDomainEvent(DomainEvent):
    transfer_id: str = ""
    origin_account_id: str = ""
    destination_pix_key: str = ""
    amount: float = 0.0


@dataclass(frozen=True)
class TransferRejectedDomainEvent(DomainEvent):
    origin_account_id: str = ""
    destination_pix_key: str = ""
    amount: float = 0.0
    reason: str = ""


class ITransfersModule(ABC):
    @abstractmethod
    def execute_pix_transfer(self, cmd: ExecutePixTransferCommand) -> TransferResultDto:
        pass
