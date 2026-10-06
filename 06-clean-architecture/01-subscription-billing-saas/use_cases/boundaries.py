"""
use_cases/boundaries.py - Camada 2: Contratos de Fronteira (Input, Output e Gateways).

Define como a camada externa invoca os casos de uso (Input Boundary),
como os casos de uso entregam dados para os apresentadores (Output Boundary)
e como os casos de uso acessam persistência e serviços (Gateways).
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional
from entities.models import Subscription, Customer, Plan
from use_cases.dto import (
    CreateSubscriptionRequestModel,
    CreateSubscriptionResponseModel,
    UpgradePlanRequestModel,
    UpgradePlanResponseModel,
    CancelSubscriptionRequestModel,
    CancelSubscriptionResponseModel,
)


# --- Input Boundaries (O que os Controllers acionam) ---

class CreateSubscriptionInputBoundary(ABC):
    @abstractmethod
    def execute(self, request: CreateSubscriptionRequestModel) -> None:
        pass


class UpgradePlanInputBoundary(ABC):
    @abstractmethod
    def execute(self, request: UpgradePlanRequestModel) -> None:
        pass


class CancelSubscriptionInputBoundary(ABC):
    @abstractmethod
    def execute(self, request: CancelSubscriptionRequestModel) -> None:
        pass


# --- Output Boundaries (O que os Presenters implementam) ---

class CreateSubscriptionOutputBoundary(ABC):
    @abstractmethod
    def present(self, response: CreateSubscriptionResponseModel) -> None:
        pass


class UpgradePlanOutputBoundary(ABC):
    @abstractmethod
    def present(self, response: UpgradePlanResponseModel) -> None:
        pass


class CancelSubscriptionOutputBoundary(ABC):
    @abstractmethod
    def present(self, response: CancelSubscriptionResponseModel) -> None:
        pass


# --- Gateways (O que a infraestrutura e repositórios implementam) ---

class SubscriptionRepositoryGateway(ABC):
    @abstractmethod
    def save(self, subscription: Subscription) -> None:
        pass

    @abstractmethod
    def find_by_id(self, subscription_id: str) -> Optional[Subscription]:
        pass


class CustomerRepositoryGateway(ABC):
    @abstractmethod
    def find_by_id(self, customer_id: str) -> Optional[Customer]:
        pass


class PlanRepositoryGateway(ABC):
    @abstractmethod
    def find_by_id(self, plan_id: str) -> Optional[Plan]:
        pass


class PaymentGateway(ABC):
    @abstractmethod
    def charge(self, token: str, amount: float, description: str) -> bool:
        pass
