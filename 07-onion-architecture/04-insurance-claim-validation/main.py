"""Ponto de Entrada e Demonstração Executável - Exemplo 04: Regulação de Sinistros de Seguros.

Demonstra a aplicação dos 4 anéis da Onion Architecture:
- Ring 1: Modelos de Domínio (Policy, Claim, DamageAssessment, ClaimSettlementDecision)
- Ring 2: Serviço de Domínio (ClaimEvaluatorDomainService)
- Ring 3: Aplicação / Casos de Uso (ClaimApplicationService, Interfaces DTOs)
- Ring 4: Infraestrutura (Repositórios em memória, MockFraudDetection, Controller)
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

# Garante que o diretório atual do exemplo seja a raiz dos imports
sys.path.insert(0, str(Path(__file__).parent))

# Ring 1 - Domain Model
from domain.model.policy import Policy, PolicyStatus, CoverageType

# Ring 2 - Domain Services
from domain.services.claim_evaluator import ClaimEvaluatorDomainService

# Ring 3 - Application
from application.claim_service import ClaimApplicationService
from application.dtos import SubmitClaimCommand, AssessClaimCommand

# Ring 4 - Infrastructure
from infrastructure.in_memory_repositories import InMemoryPolicyRepository, InMemoryClaimRepository
from infrastructure.external_adapters import MockFraudDetectionBureauGateway, MockNotificationGateway
from infrastructure.controller import InsuranceClaimsController


def main() -> None:
    print("=" * 80)
    print(" ONION ARCHITECTURE - EXEMPLO 04: INSURANCE CLAIM REGULATION & VALIDATION")
    print("=" * 80)

    # 1. Composição de Dependências (Inversão de Dependências)
    policy_repo = InMemoryPolicyRepository()
    claim_repo = InMemoryClaimRepository()
    fraud_gateway = MockFraudDetectionBureauGateway()
    notification_gateway = MockNotificationGateway()

    # Ring 2 no centro
    evaluator_service = ClaimEvaluatorDomainService()

    # Ring 3 orquestrando
    app_service = ClaimApplicationService(
        policy_repository=policy_repo,
        claim_repository=claim_repo,
        fraud_gateway=fraud_gateway,
        notification_gateway=notification_gateway,
        evaluator_service=evaluator_service,
    )

    # Ring 4 na borda externa
    controller = InsuranceClaimsController(claim_service=app_service)

    # Carga de Apólices Base
    hoje = datetime.now()
    inicio_vigencia = hoje - timedelta(days=60)
    fim_vigencia = hoje + timedelta(days=305)

    # Apólice 1: Seguro Auto Premium (LMI R$ 100.000, Franquia R$ 2.500)
    policy_auto = Policy(
        policy_id="POL_AUTO_001",
        policy_number="APO-2026-AUTO-9912",
        insured_name="Carlos Drummond",
        coverage_type=CoverageType.AUTO,
        start_date=inicio_vigencia,
        end_date=fim_vigencia,
        coverage_limit=100_000.0,
        deductible=2_500.0,
        status=PolicyStatus.ACTIVE,
    )
    policy_repo.save(policy_auto)

    # Apólice 2: Seguro Residencial Expirado
    policy_expirada = Policy(
        policy_id="POL_HOME_EXPIRED",
        policy_number="APO-2024-HOME-1001",
        insured_name="Mariana Ximenes",
        coverage_type=CoverageType.HOME,
        start_date=hoje - timedelta(days=400),
        end_date=hoje - timedelta(days=35),  # Venceu há 35 dias
        coverage_limit=350_000.0,
        deductible=1_500.0,
        status=PolicyStatus.EXPIRED,
    )
    policy_repo.save(policy_expirada)

    # Apólice 3: Seguro Frota Comercial (LMI R$ 80.000, Franquia R$ 4.000)
    policy_frota = Policy(
        policy_id="POL_FLEET_003",
        policy_number="APO-2026-FLT-5510",
        insured_name="Transportes Veloz S/A",
        coverage_type=CoverageType.AUTO,
        start_date=inicio_vigencia,
        end_date=fim_vigencia,
        coverage_limit=80_000.0,
        deductible=4_000.0,
        status=PolicyStatus.ACTIVE,
    )
    policy_repo.save(policy_frota)

    # --------------------------------------------------------------------------
    # CENÁRIO 1: Abertura e Liquidação Aprovada de Sinistro de Colisão
    # --------------------------------------------------------------------------
    print("\n--- CENÁRIO 1: Sinistro Válido Aprovado com Dedução de Franquia ---")
    aviso_1 = controller.post_submit_claim(SubmitClaimCommand(
        policy_id="POL_AUTO_001",
        insured_name="Carlos Drummond",
        occurrence_date=hoje - timedelta(days=2),
        claimed_amount=15_000.0,
        description="Colisão frontal no cruzamento com outro automóvel.",
    ))
    claim_id_1 = aviso_1["data"]["claim_id"]
    print(f"Status HTTP: {aviso_1['http_status']} | Aviso registrado: #{claim_id_1}")

    # Perito avalia e emite laudo: reparo estimado em R$ 12.000
    laudo_1 = controller.post_assess_claim(AssessClaimCommand(
        claim_id=claim_id_1,
        assessor_id="PERITO_ENG_09",
        loss_cause="COLISAO",
        estimated_repair_cost=12_000.0,
        damaged_items=["Parachoque dianteiro", "Radiador", "Farol esquerdo LED"],
        is_total_loss=False,
        evidence_urls=["s3://seguradora/fotos/pericia_001_1.jpg", "s3://seguradora/fotos/pericia_001_2.jpg"],
    ))
    print(f"Status HTTP: {laudo_1['http_status']}")
    print(json.dumps(laudo_1["data"], indent=2, ensure_ascii=False))

    # --------------------------------------------------------------------------
    # CENÁRIO 2: Sinistro Reclamado em Apólice Expirada (Rejeição de Invariante)
    # --------------------------------------------------------------------------
    print("\n--- CENÁRIO 2: Tentativa de Sinistro em Apólice Expirada ---")
    aviso_2 = controller.post_submit_claim(SubmitClaimCommand(
        policy_id="POL_HOME_EXPIRED",
        insured_name="Mariana Ximenes",
        occurrence_date=hoje - timedelta(days=1),
        claimed_amount=20_000.0,
        description="Vazamento hidráulico danificou assoalho.",
    ))
    print(f"Status HTTP: {aviso_2['http_status']} | Resposta: {aviso_2['data']}")

    # --------------------------------------------------------------------------
    # CENÁRIO 3: Sinistro com Causa Excluída Expressamente (Desgaste Natural)
    # --------------------------------------------------------------------------
    print("\n--- CENÁRIO 3: Sinistro com Risco Excluído por Contrato ---")
    aviso_3 = controller.post_submit_claim(SubmitClaimCommand(
        policy_id="POL_AUTO_001",
        insured_name="Carlos Drummond",
        occurrence_date=hoje - timedelta(days=5),
        claimed_amount=8_000.0,
        description="Quebra do sistema de amortecimento durante viagem.",
    ))
    claim_id_3 = aviso_3["data"]["claim_id"]

    laudo_3 = controller.post_assess_claim(AssessClaimCommand(
        claim_id=claim_id_3,
        assessor_id="PERITO_MEC_14",
        loss_cause="DESGASTE_NATURAL",
        estimated_repair_cost=4_200.0,
        damaged_items=["Amortecedores dianteiros com fadiga metálica"],
        is_total_loss=False,
        evidence_urls=["s3://seguradora/fotos/amortecedor_desgaste.jpg"],
    ))
    print(f"Status HTTP: {laudo_3['http_status']}")
    print(json.dumps(laudo_3["data"], indent=2, ensure_ascii=False))

    # --------------------------------------------------------------------------
    # CENÁRIO 4: Suspeita de Fraude (Discrepância Severa: Pediu 50k, Dano real 3k)
    # --------------------------------------------------------------------------
    print("\n--- CENÁRIO 4: Detecção de Suspeita de Fraude e Encaminhamento a Comitê ---")
    aviso_4 = controller.post_submit_claim(SubmitClaimCommand(
        policy_id="POL_AUTO_001",
        insured_name="Carlos Drummond",
        occurrence_date=hoje - timedelta(days=3),
        claimed_amount=50_000.0,  # Solicitou 50 mil
        description="Alegado dano estrutural severo por choque leve.",
    ))
    claim_id_4 = aviso_4["data"]["claim_id"]

    laudo_4 = controller.post_assess_claim(AssessClaimCommand(
        claim_id=claim_id_4,
        assessor_id="PERITO_AUDITOR_02",
        loss_cause="COLISAO",
        estimated_repair_cost=3_000.0,  # Perito apurou apenas 3 mil (16x menor)
        damaged_items=["Arranhão em lataria lateral"],
        is_total_loss=False,
        evidence_urls=["s3://seguradora/fotos/arranhador_leve.jpg"],
    ))
    print(f"Status HTTP: {laudo_4['http_status']}")
    print(json.dumps(laudo_4["data"], indent=2, ensure_ascii=False))

    # --------------------------------------------------------------------------
    # CENÁRIO 5: Sinistro de Perda Total Excedendo o Limite Máximo da Apólice (LMI)
    # --------------------------------------------------------------------------
    print("\n--- CENÁRIO 5: Dano Excedente ao Limite Máximo de Indenização (LMI) ---")
    aviso_5 = controller.post_submit_claim(SubmitClaimCommand(
        policy_id="POL_FLEET_003",
        insured_name="Transportes Veloz S/A",
        occurrence_date=hoje - timedelta(days=4),
        claimed_amount=120_000.0,
        description="Incêndio total do veículo de carga em rodovia.",
    ))
    claim_id_5 = aviso_5["data"]["claim_id"]

    # Prejuízo periciado: R$ 115.000. Porém o LMI é R$ 80.000 e a franquia é R$ 4.000.
    # Indenização líquida esperada: min(115000, 80000) - 4000 = R$ 76.000
    laudo_5 = controller.post_assess_claim(AssessClaimCommand(
        claim_id=claim_id_5,
        assessor_id="PERITO_INCENDIO_01",
        loss_cause="INCENDIO",
        estimated_repair_cost=115_000.0,
        damaged_items=["Chassi queimado", "Cabine calcinada", "Motor destruído"],
        is_total_loss=True,
        evidence_urls=["s3://seguradora/fotos/incendio_total.jpg"],
    ))
    print(f"Status HTTP: {laudo_5['http_status']}")
    print(json.dumps(laudo_5["data"], indent=2, ensure_ascii=False))

    # --------------------------------------------------------------------------
    # CENÁRIO 6: Auditoria de Notificações Disparadas para os Segurados
    # --------------------------------------------------------------------------
    print("\n--- CENÁRIO 6: Notificações Enviadas pelo Gateway de Infraestrutura ---")
    for notif in notification_gateway.sent_notifications[:4]:
        print(f" -> {notif}")

    print("\n" + "=" * 80)
    print(" Exemplo 04 de Onion Architecture finalizado com sucesso!")
    print("=" * 80)


if __name__ == "__main__":
    main()
