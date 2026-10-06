"""
use_cases/interactors.py - Camada 2: Interactors (Orquestradores de Casos de Uso).

Implementam os Input Boundaries, coordenam entidades de domínio e
enviam o resultado formatado em DTO para os Output Boundaries (Presenters).
"""

from __future__ import annotations
import uuid
from datetime import datetime, timezone, timedelta
from entities.models import Subscription, SubscriptionStatus, BillingCycle
from use_cases.dto import (
    CreateSubscriptionRequestModel,
    CreateSubscriptionResponseModel,
    UpgradePlanRequestModel,
    UpgradePlanResponseModel,
    CancelSubscriptionRequestModel,
    CancelSubscriptionResponseModel,
)
from use_cases.boundaries import (
    CreateSubscriptionInputBoundary,
    CreateSubscriptionOutputBoundary,
    UpgradePlanInputBoundary,
    UpgradePlanOutputBoundary,
    CancelSubscriptionInputBoundary,
    CancelSubscriptionOutputBoundary,
    SubscriptionRepositoryGateway,
    CustomerRepositoryGateway,
    PlanRepositoryGateway,
    PaymentGateway,
)


class CreateSubscriptionInteractor(CreateSubscriptionInputBoundary):
    def __init__(
        self,
        customer_repo: CustomerRepositoryGateway,
        plan_repo: PlanRepositoryGateway,
        subscription_repo: SubscriptionRepositoryGateway,
        payment_gateway: PaymentGateway,
        presenter: CreateSubscriptionOutputBoundary,
    ) -> None:
        self.customer_repo = customer_repo
        self.plan_repo = plan_repo
        self.subscription_repo = subscription_repo
        self.payment_gateway = payment_gateway
        self.presenter = presenter

    def execute(self, request: CreateSubscriptionRequestModel) -> None:
        # 1. Busca Cliente
        customer = self.customer_repo.find_by_id(request.customer_id)
        if not customer:
            self.presenter.present(CreateSubscriptionResponseModel(
                success=False,
                subscription_id=None,
                customer_name=None,
                plan_name=None,
                cycle=None,
                amount_charged=0.0,
                next_billing_date=None,
                message=f"Cliente '{request.customer_id}' não encontrado.",
            ))
            return

        # 2. Busca Plano
        plan = self.plan_repo.find_by_id(request.plan_id)
        if not plan:
            self.presenter.present(CreateSubscriptionResponseModel(
                success=False,
                subscription_id=None,
                customer_name=customer.name,
                plan_name=None,
                cycle=None,
                amount_charged=0.0,
                next_billing_date=None,
                message=f"Plano '{request.plan_id}' não localizado no catálogo.",
            ))
            return

        # 3. Determina Ciclo e Preço
        cycle = BillingCycle.ANNUALLY if request.cycle == "ANNUALLY" else BillingCycle.MONTHLY
        price = plan.get_price_for_cycle(cycle)

        # 4. Cobrança no Gateway
        charge_success = self.payment_gateway.charge(
            token=customer.payment_method_token,
            amount=price,
            description=f"Assinatura SaaS {plan.name} ({cycle.value})",
        )
        if not charge_success:
            self.presenter.present(CreateSubscriptionResponseModel(
                success=False,
                subscription_id=None,
                customer_name=customer.name,
                plan_name=plan.name,
                cycle=cycle.value,
                amount_charged=0.0,
                next_billing_date=None,
                message="Falha na autorização do cartão de crédito pelo gateway.",
            ))
            return

        # 5. Cria Entidade Subscription
        now = datetime.now(timezone.utc)
        cycle_days = 365 if cycle == BillingCycle.ANNUALLY else 30
        end_date = now + timedelta(days=cycle_days)

        sub_id = f"sub_{uuid.uuid4().hex[:8]}"
        subscription = Subscription(
            subscription_id=sub_id,
            customer_id=customer.customer_id,
            plan=plan,
            cycle=cycle,
            status=SubscriptionStatus.ACTIVE,
            current_period_start=now,
            current_period_end=end_date,
        )

        # 6. Salva no Repositório
        self.subscription_repo.save(subscription)

        # 7. Dispara Apresentação (Output Boundary)
        self.presenter.present(CreateSubscriptionResponseModel(
            success=True,
            subscription_id=sub_id,
            customer_name=customer.name,
            plan_name=plan.name,
            cycle=cycle.value,
            amount_charged=price,
            next_billing_date=end_date.strftime("%Y-%m-%d"),
            message="Assinatura criada e ativada com sucesso!",
        ))


class UpgradePlanInteractor(UpgradePlanInputBoundary):
    def __init__(
        self,
        subscription_repo: SubscriptionRepositoryGateway,
        plan_repo: PlanRepositoryGateway,
        customer_repo: CustomerRepositoryGateway,
        payment_gateway: PaymentGateway,
        presenter: UpgradePlanOutputBoundary,
    ) -> None:
        self.subscription_repo = subscription_repo
        self.plan_repo = plan_repo
        self.customer_repo = customer_repo
        self.payment_gateway = payment_gateway
        self.presenter = presenter

    def execute(self, request: UpgradePlanRequestModel) -> None:
        # 1. Localiza assinatura
        subscription = self.subscription_repo.find_by_id(request.subscription_id)
        if not subscription:
            self.presenter.present(UpgradePlanResponseModel(
                success=False,
                subscription_id=request.subscription_id,
                old_plan_name=None,
                new_plan_name=None,
                unused_credit=0.0,
                prorated_amount_charged=0.0,
                message=f"Assinatura '{request.subscription_id}' não localizada.",
            ))
            return

        if not subscription.is_active():
            self.presenter.present(UpgradePlanResponseModel(
                success=False,
                subscription_id=subscription.subscription_id,
                old_plan_name=subscription.plan.name,
                new_plan_name=None,
                unused_credit=0.0,
                prorated_amount_charged=0.0,
                message="Não é permitido upgrade em assinatura inativa ou cancelada.",
            ))
            return

        # 2. Localiza novo plano
        new_plan = self.plan_repo.find_by_id(request.new_plan_id)
        if not new_plan:
            self.presenter.present(UpgradePlanResponseModel(
                success=False,
                subscription_id=subscription.subscription_id,
                old_plan_name=subscription.plan.name,
                new_plan_name=None,
                unused_credit=0.0,
                prorated_amount_charged=0.0,
                message=f"Novo plano '{request.new_plan_id}' não encontrado.",
            ))
            return

        # 3. Invoca Regra Corporativa de Domínio (Proration) na Entidade
        now = datetime.now(timezone.utc)
        unused_credit, new_price, net_to_charge = subscription.calculate_proration_credit(new_plan, now)

        # 4. Fatura a diferença residual se for maior que zero
        if net_to_charge > 0:
            customer = self.customer_repo.find_by_id(subscription.customer_id)
            if not customer:
                self.presenter.present(UpgradePlanResponseModel(
                    success=False,
                    subscription_id=subscription.subscription_id,
                    old_plan_name=subscription.plan.name,
                    new_plan_name=new_plan.name,
                    unused_credit=unused_credit,
                    prorated_amount_charged=0.0,
                    message="Dados de faturamento do cliente não localizados.",
                ))
                return

            charged = self.payment_gateway.charge(
                token=customer.payment_method_token,
                amount=net_to_charge,
                description=f"Upgrade Prorated para {new_plan.name}",
            )
            if not charged:
                self.presenter.present(UpgradePlanResponseModel(
                    success=False,
                    subscription_id=subscription.subscription_id,
                    old_plan_name=subscription.plan.name,
                    new_plan_name=new_plan.name,
                    unused_credit=unused_credit,
                    prorated_amount_charged=0.0,
                    message="Cobrança proporcional de upgrade recusada pelo gateway.",
                ))
                return

        # 5. Aplica a mudança na Entidade e persiste
        old_name = subscription.plan.name
        subscription.upgrade_plan(new_plan, now)
        self.subscription_repo.save(subscription)

        # 6. Apresentação (Output Boundary)
        self.presenter.present(UpgradePlanResponseModel(
            success=True,
            subscription_id=subscription.subscription_id,
            old_plan_name=old_name,
            new_plan_name=new_plan.name,
            unused_credit=unused_credit,
            prorated_amount_charged=net_to_charge,
            message="Upgrade de plano concluído com sucesso e proration aplicada!",
        ))


class CancelSubscriptionInteractor(CancelSubscriptionInputBoundary):
    def __init__(
        self,
        subscription_repo: SubscriptionRepositoryGateway,
        presenter: CancelSubscriptionOutputBoundary,
    ) -> None:
        self.subscription_repo = subscription_repo
        self.presenter = presenter

    def execute(self, request: CancelSubscriptionRequestModel) -> None:
        sub = self.subscription_repo.find_by_id(request.subscription_id)
        if not sub:
            self.presenter.present(CancelSubscriptionResponseModel(
                success=False,
                subscription_id=request.subscription_id,
                cancelled_at=None,
                message=f"Assinatura '{request.subscription_id}' inexistente.",
            ))
            return

        now = datetime.now(timezone.utc)
        sub.cancel(now)
        self.subscription_repo.save(sub)

        self.presenter.present(CancelSubscriptionResponseModel(
            success=True,
            subscription_id=sub.subscription_id,
            cancelled_at=now.strftime("%Y-%m-%d %H:%M:%S UTC"),
            message="Assinatura cancelada com sucesso.",
        ))
