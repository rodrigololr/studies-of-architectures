"""
main.py - Camada 4: Frameworks & Drivers (Composition Root).
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from entities.models import SalesRep, RepTier
from interface_adapters.gateways import (
    InMemoryLeadRepository,
    MockFirmographicGateway,
    InMemorySalesRepRepository,
)
from interface_adapters.presenters import LeadQualificationPresenter
from interface_adapters.controllers import LeadIngestionController
from use_cases.interactors import IngestLeadInteractor


def main() -> None:
    print("=" * 80)
    print(" CLEAN ARCHITECTURE - EXEMPLO 06: CRM LEAD ENRICHMENT & SCORING PIPELINE")
    print("=" * 80)

    # 1. Configuração de Equipe de Vendas e Infraestrutura
    rep_repo = InMemorySalesRepRepository({
        "rep_01": SalesRep("rep_01", "Mariana Ramos", RepTier.ENTERPRISE),
        "rep_02": SalesRep("rep_02", "Felipe Alcantara", RepTier.MID_MARKET),
        "rep_03": SalesRep("rep_03", "Gabriel Soares", RepTier.SMB),
    })

    lead_repo = InMemoryLeadRepository()
    firmographic_gw = MockFirmographicGateway()
    presenter = LeadQualificationPresenter()

    # 2. Montagem dos Casos de Uso
    interactor = IngestLeadInteractor(
        lead_repo=lead_repo,
        firmographic_gateway=firmographic_gw,
        rep_repo=rep_repo,
        presenter=presenter,
    )
    controller = LeadIngestionController(ingest_use_case=interactor)

    print("\n--- CENÁRIO 1: Ingestão de Lead Enterprise (CTO de Grande Empresa) -> HOT ---")
    controller.handle_post_lead({
        "name": "Dr. Fernando Henrique",
        "email": "fernando.cto@techcorp.com",
        "company": "TechCorp SA",
        "job_title": "Chief Technology Officer (CTO)",
    })
    print(f"HTTP Status: {presenter.status_code}")
    print(json.dumps(presenter.response_body, indent=2, ensure_ascii=False))

    print("\n--- CENÁRIO 2: Ingestão de Lead Mid-Market (Gerente de TI) -> WARM ---")
    controller.handle_post_lead({
        "name": "Roberta Mendonça",
        "email": "roberta.ti@varejodigital.com.br",
        "company": "Varejo Digital",
        "job_title": "Gerente de Infraestrutura de TI",
    })
    print(f"HTTP Status: {presenter.status_code}")
    print(json.dumps(presenter.response_body, indent=2, ensure_ascii=False))

    print("\n--- CENÁRIO 3: Ingestão de Lead SMB / Microempresa -> COLD ---")
    controller.handle_post_lead({
        "name": "Joãozinho da Padaria",
        "email": "contato@padariadobairro.com.br",
        "company": "Padaria do Bairro",
        "job_title": "Atendente",
    })
    print(f"HTTP Status: {presenter.status_code}")
    print(json.dumps(presenter.response_body, indent=2, ensure_ascii=False))

    print("\n--- CENÁRIO 4: Rejeição de E-mail Pessoal Gratuito (@gmail.com) ---")
    controller.handle_post_lead({
        "name": "Curioso Sem Empresa",
        "email": "curioso123@gmail.com",
        "company": "Freelancer",
        "job_title": "Estudante",
    })
    print(f"HTTP Status: {presenter.status_code}")
    print(json.dumps(presenter.response_body, indent=2, ensure_ascii=False))

    print("\n" + "=" * 80)
    print(" Exemplo 06 finalizado com sucesso!")
    print("=" * 80)


if __name__ == "__main__":
    main()
