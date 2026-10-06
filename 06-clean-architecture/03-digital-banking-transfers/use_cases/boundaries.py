"""
use_cases/boundaries.py - Camada 2: Boundaries e Gateways.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, List
from entities.models import Account, Transfer, PixKeyRecord
from use_cases.dto import TransferFundsRequestModel, TransferFundsResponseModel


class TransferFundsInputBoundary(ABC):
    @abstractmethod
    def execute(self, request: TransferFundsRequestModel) -> None:
        pass


class TransferFundsOutputBoundary(ABC):
    @abstractmethod
    def present(self, response: TransferFundsResponseModel) -> None:
        pass


class AccountRepositoryGateway(ABC):
    @abstractmethod
    def find_by_account_number(self, account_number: str) -> Optional[Account]:
        pass

    @abstractmethod
    def save(self, account: Account) -> None:
        pass


class PixDirectoryGateway(ABC):
    @abstractmethod
    def lookup_pix_key(self, pix_key: str) -> Optional[PixKeyRecord]:
        """Consulta o Diretório de Identificadores de Contas Transacionais (DICT Bacen)."""
        pass


class TransferRepositoryGateway(ABC):
    @abstractmethod
    def save(self, transfer: Transfer) -> None:
        pass

    @abstractmethod
    def list_by_account(self, account_number: str) -> List[Transfer]:
        pass
