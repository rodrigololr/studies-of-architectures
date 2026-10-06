"""
interface_adapters/gateways.py - Camada 3: Interface Adapters (Gateways & Repositories).

Implementam os contratos de persistência e serviços externos definidos na camada Use Cases.
"""

from __future__ import annotations
from typing import Dict, Optional
from entities.models import Subscription, Customer, Plan
from use_cases.boundaries import (
    SubscriptionRepositoryGateway,
    CustomerRepositoryGateway,
    PlanRepositoryGateway,
    PaymentGateway,
)


class InMemorySubscriptionRepository(SubscriptionRepositoryGateway):
    def __init__(self) -> None:
        self._subscriptions: Dict[str, Subscription] = {}

    def save(self, subscription: Subscription) -> None:
        self._subscriptions[subscription.subscription_id] = subscription

    def find_by_id(self, subscription_id: str) -> Optional[Subscription]:
        return self._subscriptions.get(subscription_id)


class InMemoryCustomerRepository(CustomerRepositoryGateway):
    def __init__(self, initial_customers: Optional[Dict[str, Customer]] = None) -> None:
        self._customers: Dict[str, Customer] = dict(initial_customers or {})

    def add_customer(self, customer: Customer) -> None:
        self._customers[customer.customer_id] = customer

    def find_by_id(self, customer_id: str) -> Optional[Customer]:
        return self._customers.get(customer_id)


class InMemoryPlanRepository(PlanRepositoryGateway):
    def __init__(self, initial_plans: Optional[Dict[str, Plan]] = None) -> None:
        self._plans: Dict[str, Plan] = dict(initial_plans or {})

    def add_plan(self, plan: Plan) -> None:
        self._plans[plan.plan_id] = plan

    def find_by_id(self, plan_id: str) -> Optional[Plan]:
        return self._plans.get(plan_id)


class MockStripePaymentGateway(PaymentGateway):
    def __init__(self, should_succeed: bool = True) -> None:
        self.should_succeed = should_succeed
        self.transactions: list[tuple[str, float, str]] = []

    def charge(self, token: str, amount: float, description: str) -> bool:
        if not self.should_succeed or token == "tok_fail":
            return False
        self.transactions.append((token, amount, description))
        return True
