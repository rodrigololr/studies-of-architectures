"""Ponto de Entrada e Demonstração Executável - Exemplo 03: SaaS Multi-Tenant CRM.

Demonstra:
1. Módulos com Bounded Contexts em monólito: Identity, Subscriptions, Leads, Audit.
2. Controle de limites de uso e cotas de plano (Feature Toggling / Quota Limits) através de contratos públicos.
3. Trilha de auditoria append-only consolidada via eventos intra-processo.
"""

import sys
import json
from pathlib import Path

# Adiciona diretório do exemplo ao sys.path
sys.path.insert(0, str(Path(__file__).parent))

from shared.events import InProcessEventBus
from modules.identity import IdentityModule, RegisterTenantCommand
from modules.subscriptions import SubscriptionsModule, ChangePlanCommand
from modules.leads import LeadsModule, CreateLeadCommand, QuotaExceededError
from modules.audit import AuditModule


def main() -> None:
    print("=" * 80)
    print(" MODULAR MONOLITH - EXEMPLO 03: SAAS MULTI-TENANT CRM")
    print("=" * 80)

    # 1. Composição de Módulos e Barramento
    event_bus = InProcessEventBus()

    identity = IdentityModule(event_bus=event_bus)
    subscriptions = SubscriptionsModule(event_bus=event_bus)
    leads = LeadsModule(
        identity_module=identity,
        subscriptions_module=subscriptions,
        event_bus=event_bus,
    )
    audit = AuditModule(event_bus=event_bus)

    # --------------------------------------------------------------------------
    # CENÁRIO 1: Registro de Novo Tenant (Acme Corp) no Plano Starter
    # --------------------------------------------------------------------------
    print("\n--- CENÁRIO 1: Onboarding de Novo Tenant (Plano STARTER) ---")
    tenant_acme = identity.register_tenant(RegisterTenantCommand(
        company_name="Acme Corporation",
        admin_email="admin@acme.com",
        initial_plan="STARTER",
    ))
    limits = subscriptions.get_plan_limits(tenant_acme.tenant_id)
    print(f"Tenant Criado: {tenant_acme.company_name} (ID: {tenant_acme.tenant_id})")
    print(f"Plano Ativo: {limits.plan_name} | Cota Máxima: {limits.max_leads} leads | Mensalidade: R$ {limits.monthly_price:,.2f}")

    # --------------------------------------------------------------------------
    # CENÁRIO 2: Cadastro de Leads dentro da Cota do Plano
    # --------------------------------------------------------------------------
    print("\n--- CENÁRIO 2: Cadastro de Oportunidades / Leads ---")
    lead_1 = leads.create_lead(CreateLeadCommand(
        tenant_id=tenant_acme.tenant_id,
        contact_name="Pedro Álvares",
        contact_email="pedro@porto.com",
        estimated_value=15_000.0,
    ))
    lead_2 = leads.create_lead(CreateLeadCommand(
        tenant_id=tenant_acme.tenant_id,
        contact_name="Ana Néri",
        contact_email="ana@saude.com",
        estimated_value=32_000.0,
    ))
    lead_3 = leads.create_lead(CreateLeadCommand(
        tenant_id=tenant_acme.tenant_id,
        contact_name="Santos Dumont",
        contact_email="santos@aero.com",
        estimated_value=50_000.0,
    ))
    print(f" -> Lead 1: {lead_1.contact_name} (R$ {lead_1.estimated_value:,.2f}) - Status: {lead_1.status}")
    print(f" -> Lead 2: {lead_2.contact_name} (R$ {lead_2.estimated_value:,.2f}) - Status: {lead_2.status}")
    print(f" -> Lead 3: {lead_3.contact_name} (R$ {lead_3.estimated_value:,.2f}) - Status: {lead_3.status}")
    print(f"Total de leads cadastrados: {leads.count_leads(tenant_acme.tenant_id)} de {limits.max_leads} permitidos.")

    # --------------------------------------------------------------------------
    # CENÁRIO 3: Violação de Cota do Plano (Bloqueio Automático)
    # --------------------------------------------------------------------------
    print("\n--- CENÁRIO 3: Tentativa de Estourar Cota de Leads (4º Lead no Plano Starter) ---")
    try:
        leads.create_lead(CreateLeadCommand(
            tenant_id=tenant_acme.tenant_id,
            contact_name="Oswaldo Cruz",
            contact_email="oswaldo@fiocruz.com",
            estimated_value=12_000.0,
        ))
    except QuotaExceededError as e:
        print(f"Bloqueio com sucesso pela regra de negócio: {e}")

    # --------------------------------------------------------------------------
    # CENÁRIO 4: Upgrade de Plano (STARTER -> PRO)
    # --------------------------------------------------------------------------
    print("\n--- CENÁRIO 4: Upgrade de Assinatura para o Plano PRO ---")
    new_limits = subscriptions.change_plan(ChangePlanCommand(
        tenant_id=tenant_acme.tenant_id,
        new_plan="PRO",
    ))
    print(f"Upgrade Concluído! Novo Plano: {new_limits.plan_name} | Nova Cota: {new_limits.max_leads} leads | Mensalidade: R$ {new_limits.monthly_price:,.2f}")

    # Agora a inclusão do 4º lead deve funcionar perfeitamente
    lead_4 = leads.create_lead(CreateLeadCommand(
        tenant_id=tenant_acme.tenant_id,
        contact_name="Oswaldo Cruz",
        contact_email="oswaldo@fiocruz.com",
        estimated_value=12_000.0,
    ))
    print(f" -> Lead 4 cadastrado com sucesso após upgrade: {lead_4.contact_name} (R$ {lead_4.estimated_value:,.2f})")

    # --------------------------------------------------------------------------
    # CENÁRIO 5: Auditoria Append-Only Consolidada via Eventos
    # --------------------------------------------------------------------------
    print("\n--- CENÁRIO 5: Trilha de Auditoria do Tenant (Módulo Audit) ---")
    logs = audit.list_logs_for_tenant(tenant_acme.tenant_id)
    print(f"Total de registros de auditoria capturados: {len(logs)}")
    for idx, log in enumerate(logs, start=1):
        print(f"  {idx}. [{log.timestamp.strftime('%H:%M:%S')}] [{log.event_type}] {log.summary}")

    print("\n" + "=" * 80)
    print(" Exemplo 03 de Modular Monolith finalizado com sucesso!")
    print("=" * 80)


if __name__ == "__main__":
    main()
