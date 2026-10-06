"""
main.py - Composition Root e Demonstração do Exemplo 04.
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.service import CreditUnderwritingService
from adapters.secondary.serasa_bureau_adapter import SerasaBureauAdapter
from adapters.secondary.spc_bureau_adapter import SpcBureauAdapter
from adapters.secondary.bacen_scr_adapter import BacenScrAdapter
from adapters.secondary.market_rate_policy_adapter import BacenMarketRatePolicyAdapter
from adapters.secondary.in_memory_dossier_adapter import InMemoryCreditDossierAdapter
from adapters.primary.loan_application_api_controller import LoanApplicationApiController
from adapters.primary.bank_teller_console_adapter import BankTellerConsoleAdapter


def main() -> None:
    print("=" * 80)
    print(" HEXAGONAL ARCHITECTURE - EXEMPLO 04: LOAN CREDIT ANALYSIS")
    print("=" * 80)

    # 1. Adaptadores Secundários (Driven)
    # Formato do mock: CPF -> (score, tem_inadimplencia_ativa)
    serasa_db = {
        "111.222.333-44": (920, False),  # Cliente Excelente
        "222.333.444-55": (350, True),   # Cliente Negativado
        "333.444.555-66": (650, False),  # Cliente Regular
        "444.555.666-77": (810, False),  # Cliente Balcão Agência
    }
    spc_db = {
        "111.222.333-44": (910, False),
        "222.333.444-55": (320, True),
        "333.444.555-66": (630, False),
        "444.555.666-77": (790, False),
    }
    bacen_db = {
        "111.222.333-44": 1500.0,
        "222.333.444-55": 45000.0,
        "333.444.555-66": 8000.0,
        "444.555.666-77": 0.0,
    }

    serasa_adapter = SerasaBureauAdapter(serasa_db)
    spc_adapter = SpcBureauAdapter(spc_db)
    bacen_adapter = BacenScrAdapter(bacen_db)
    rate_policy_adapter = BacenMarketRatePolicyAdapter()
    dossier_repo = InMemoryCreditDossierAdapter()

    # 2. Núcleo da Aplicação (Core / Hexágono)
    underwriting_service = CreditUnderwritingService(
        bureaus=[serasa_adapter, spc_adapter],
        bacen_scr=bacen_adapter,
        rate_policy=rate_policy_adapter,
        dossier_repo=dossier_repo,
    )

    # 3. Adaptadores Primários (Driver)
    api_controller = LoanApplicationApiController(
        underwrite_use_case=underwriting_service,
        dossier_use_case=underwriting_service,
    )
    teller_console = BankTellerConsoleAdapter(
        underwrite_use_case=underwriting_service,
        branch_id="0042-PAULISTA",
    )

    print("\n--- CENÁRIO 1: Cliente Excelente -> Aprovado Rating AAA ---")
    status, res = api_controller.handle_submit_proposal({
        "proposal_id": "PROP-2026-001",
        "applicant": {
            "cpf": "111.222.333-44",
            "name": "Dr. Fernando Noronha",
            "income": 25000.0,
            "birth_date": "1980-04-12",
        },
        "amount": 50000.0,
        "installments": 24,
    })
    print(f"Status HTTP: {status}")
    print(json.dumps(res, indent=2, ensure_ascii=False))

    print("\n--- CENÁRIO 2: Cliente com Restrição Ativa (Inadimplência) -> Reprovação Imediata ---")
    status, res = api_controller.handle_submit_proposal({
        "proposal_id": "PROP-2026-002",
        "applicant": {
            "cpf": "222.333.444-55",
            "name": "Joaquim Inadimplente",
            "income": 8000.0,
            "birth_date": "1992-09-20",
        },
        "amount": 10000.0,
        "installments": 12,
    })
    print(f"Status HTTP: {status}")
    print(json.dumps(res, indent=2, ensure_ascii=False))

    print("\n--- CENÁRIO 3: Parcela Excede 30% da Renda -> Reprovação por Capacidade Financeira ---")
    status, res = api_controller.handle_submit_proposal({
        "proposal_id": "PROP-2026-003",
        "applicant": {
            "cpf": "333.444.555-66",
            "name": "Luciana Santos",
            "income": 4000.0,  # 30% = R$ 1.200,00 teto
            "birth_date": "1995-11-03",
        },
        "amount": 80000.0,  # Parcela de 80k em 24x supera em muito R$ 1.200
        "installments": 24,
    })
    print(f"Status HTTP: {status}")
    print(json.dumps(res, indent=2, ensure_ascii=False))

    print("\n--- CENÁRIO 4: Atendimento Presencial via Terminal do Gerente de Agência ---")
    teller_msg = teller_console.process_counter_proposal(
        cpf="444.555.666-77",
        name="Patrícia Guimarães",
        income=12000.0,
        amount=30000.0,
        installments=36,
    )
    print(teller_msg)

    print("\n--- CENÁRIO 5: Rejeição de Proposta Inválida (Regra de Domínio) ---")
    status, res = api_controller.handle_submit_proposal({
        "proposal_id": "PROP-INV-001",
        "applicant": {
            "cpf": "000.000.000-00",
            "name": "Teste Inválido",
            "income": -500.0,
        },
        "amount": 1000.0,
        "installments": 12,
    })
    print(f"Status HTTP: {status} | Resposta: {res}")

    print("\n--- CENÁRIO 6: Consulta de Dossiê Gravado no Repositório Secundário ---")
    dossier = underwriting_service.get_dossier("PROP-2026-001")
    if dossier:
        print(f"Dossiê #{dossier.proposal_id} localizado no banco:")
        print(f" -> Decisão: {dossier.decision.value} | Rating: {dossier.risk_rating.value}")
        print(f" -> Valor Aprovado: R$ {dossier.approved_amount:.2f} | Parcela: R$ {dossier.monthly_installment:.2f}")

    print("\n" + "=" * 80)
    print(" Exemplo 04 finalizado com sucesso!")
    print("=" * 80)


if __name__ == "__main__":
    main()
