"""
main.py - Camada 4: Frameworks & Drivers (Composition Root).

Ponto de entrada que monta o grafo de dependências da Clean Architecture,
injetando gateways e presenters nos casos de uso, e casos de uso nos controllers.
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from entities.models import Customer, Plan
from interface_adapters.gateways import (
    InMemoryCustomerRepository,
    InMemoryPlanRepository,
    InMemorySubscriptionRepository,
    MockStripePaymentGateway,
)
from interface_adapters.presenters import SubscriptionRestPresenter
from interface_adapters.controllers import SubscriptionWebController
from use_cases.interactors import (
    CreateSubscriptionInteractor,
    UpgradePlanInteractor,
    CancelSubscriptionInteractor,
)


def main() -> None:
    print("=" * 80)
    print(" CLEAN ARCHITECTURE - EXEMPLO 01: SUBSCRIPTION BILLING SAAS")
    print("=" * 80)

    # 1. Configuração do Catálogo de Planos e Clientes (Entidades)
    starter_plan = Plan(
        plan_id="plan_starter",
        name="Starter",
        monthly_price=29.0,
        annual_price=290.0,
        max_seats=5,
        features=["Kanban", "Exportação Básica"],
    )
    pro_plan = Plan(
        plan_id="plan_pro",
        name="Professional",
        monthly_price=99.0,
        annual_price=990.0,
        max_seats=20,
        features=["Kanban", "Relatórios Avançados", "Suporte 24/7"],
    )
    enterprise_plan = Plan(
        plan_id="plan_enterprise",
        name="Enterprise",
        monthly_price=299.0,
        annual_price=2990.0,
        max_seats=100,
        features=["Tudo do Pro", "SSO SAML", "Gerente de Contas Dedicado"],
    )

    customer_repo = InMemoryCustomerRepository({
        "cust_acme": Customer(
            customer_id="cust_acme",
            name="Acme Corporation",
            email="financeiro@acme.com",
            payment_method_token="tok_visa_valid_9988",
        ),
        "cust_broken": Customer(
            customer_id="cust_broken",
            name="Broke Startup",
            email="billing@broke.io",
            payment_method_token="tok_fail",
        ),
    })

    plan_repo = InMemoryPlanRepository({
        starter_plan.plan_id: starter_plan,
        pro_plan.plan_id: pro_plan,
        enterprise_plan.plan_id: enterprise_plan,
    })

    sub_repo = InMemorySubscriptionRepository()
    payment_gw = MockStripePaymentGateway()

    # 2. Camada 3: Interface Adapters (Presenters)
    presenter = SubscriptionRestPresenter()

    # 3. Camada 2: Use Cases (Interactors)
    create_use_case = CreateSubscriptionInteractor(
        customer_repo=customer_repo,
        plan_repo=plan_repo,
        subscription_repo=sub_repo,
        payment_gateway=payment_gw,
        presenter=presenter,
    )
    upgrade_use_case = UpgradePlanInteractor(
        subscription_repo=sub_repo,
        plan_repo=plan_repo,
        customer_repo=customer_repo,
        payment_gateway=payment_gw,
        presenter=presenter,
    )
    cancel_use_case = CancelSubscriptionInteractor(
        subscription_repo=sub_repo,
        presenter=presenter,
    )

    # 4. Camada 3: Interface Adapters (Controllers)
    controller = SubscriptionWebController(
        create_use_case=create_use_case,
        upgrade_use_case=upgrade_use_case,
        cancel_use_case=cancel_use_case,
    )

    print("\n--- CENÁRIO 1: Criação de Nova Assinatura Mensal (Plano Pro) ---")
    controller.post_subscribe({
        "customer_id": "cust_acme",
        "plan_id": "plan_pro",
        "billing_cycle": "MONTHLY",
    })
    print(f"HTTP Status: {presenter.last_status_code}")
    print(json.dumps(presenter.last_response_data, indent=2, ensure_ascii=False))

    sub_id = presenter.last_response_data["data"]["subscription_id"]

    print("\n--- CENÁRIO 2: Upgrade com Cálculo Corporativo de Proration (Pro -> Enterprise) ---")
    controller.put_upgrade({
        "subscription_id": sub_id,
        "new_plan_id": "plan_enterprise",
    })
    print(f"HTTP Status: {presenter.last_status_code}")
    print(json.dumps(presenter.last_response_data, indent=2, ensure_ascii=False))

    print("\n--- CENÁRIO 3: Falha na Cobrança de Cartão Recusado ---")
    controller.post_subscribe({
        "customer_id": "cust_broken",
        "plan_id": "plan_starter",
        "billing_cycle": "MONTHLY",
    })
    print(f"HTTP Status: {presenter.last_status_code}")
    print(json.dumps(presenter.last_response_data, indent=2, ensure_ascii=False))

    print("\n--- CENÁRIO 4: Validação de Caso de Uso (Plano Inexistente) ---")
    controller.post_subscribe({
        "customer_id": "cust_acme",
        "plan_id": "plan_inexistente_xyz",
        "billing_cycle": "MONTHLY",
    })
    print(f"HTTP Status: {presenter.last_status_code}")
    print(json.dumps(presenter.last_response_data, indent=2, ensure_ascii=False))

    print("\n--- CENÁRIO 5: Cancelamento de Assinatura Ativa ---")
    controller.post_cancel({
        "subscription_id": sub_id,
        "reason": "Redução de custos operacionais",
    })
    print(f"HTTP Status: {presenter.last_status_code}")
    print(json.dumps(presenter.last_response_data, indent=2, ensure_ascii=False))

    print("\n--- CENÁRIO 6: Bloqueio de Upgrade em Assinatura Cancelada ---")
    controller.put_upgrade({
        "subscription_id": sub_id,
        "new_plan_id": "plan_pro",
    })
    print(f"HTTP Status: {presenter.last_status_code}")
    print(json.dumps(presenter.last_response_data, indent=2, ensure_ascii=False))

    print("\n" + "=" * 80)
    print(" Demonstração concluída! Clean Architecture mantendo 100% do desacoplamento.")
    print("=" * 80)


if __name__ == "__main__":
    main()
