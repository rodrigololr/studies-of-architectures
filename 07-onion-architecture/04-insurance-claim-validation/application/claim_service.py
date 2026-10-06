"""Application Service: Coordenação de casos de uso de regulação de sinistros."""

import uuid
from datetime import datetime
from application.interfaces import IPolicyRepository, IClaimRepository, IFraudDetectionGateway, INotificationGateway
from application.dtos import SubmitClaimCommand, SubmitClaimResponse, AssessClaimCommand, SettleClaimResponse
from domain.model.claim import Claim, ClaimStatus
from domain.model.damage_assessment import DamageAssessment
from domain.model.exceptions import InsuranceDomainException
from domain.services.claim_evaluator import ClaimEvaluatorDomainService


class ClaimApplicationService:
    """Caso de Uso / Serviço de Aplicação (Ring 3 da Onion Architecture).
    
    Orquestra fluxo de aviso e liquidação de sinistros, delegando regras de
    cálculo ao Domain Service e persistência às interfaces injetadas.
    """

    def __init__(
        self,
        policy_repository: IPolicyRepository,
        claim_repository: IClaimRepository,
        fraud_gateway: IFraudDetectionGateway,
        notification_gateway: INotificationGateway,
        evaluator_service: ClaimEvaluatorDomainService,
    ) -> None:
        self._policy_repo = policy_repository
        self._claim_repo = claim_repository
        self._fraud_gateway = fraud_gateway
        self._notification_gateway = notification_gateway
        self._evaluator_service = evaluator_service

    def submit_claim(self, cmd: SubmitClaimCommand) -> SubmitClaimResponse:
        """Abre aviso de sinistro e verifica preliminarmente a existência da apólice."""
        policy = self._policy_repo.get_by_id(cmd.policy_id)
        if not policy:
            raise InsuranceDomainException(f"Apólice com ID '{cmd.policy_id}' não localizada.")

        # Valida vigência logo no aviso
        policy.validate_eligibility_for_event(cmd.occurrence_date)

        claim_id = f"CLM_{uuid.uuid4().hex[:8].upper()}"
        claim = Claim(
            claim_id=claim_id,
            policy_id=policy.policy_id,
            insured_name=cmd.insured_name,
            occurrence_date=cmd.occurrence_date,
            claimed_amount=cmd.claimed_amount,
            description=cmd.description,
            status=ClaimStatus.SUBMITTED,
        )

        self._claim_repo.save(claim)
        self._notification_gateway.notify_insured(
            cmd.insured_name,
            f"Seu aviso de sinistro #{claim_id} foi recebido e aguarda vistoria técnica."
        )

        return SubmitClaimResponse(
            claim_id=claim_id,
            status=claim.status.value,
            message="Aviso de sinistro cadastrado com sucesso."
        )

    def assess_and_settle_claim(self, cmd: AssessClaimCommand) -> SettleClaimResponse:
        """Processa o laudo da perícia, executa o cálculo de liquidação e notifica o segurado."""
        claim = self._claim_repo.get_by_id(cmd.claim_id)
        if not claim:
            raise InsuranceDomainException(f"Sinistro #{cmd.claim_id} não encontrado.")

        policy = self._policy_repo.get_by_id(claim.policy_id)
        if not policy:
            raise InsuranceDomainException(f"Apólice vinculada #{claim.policy_id} não encontrada.")

        # Cria relatório técnico do perito
        assessment = DamageAssessment(
            assessor_id=cmd.assessor_id,
            assessment_date=datetime.now(),
            loss_cause=cmd.loss_cause,
            estimated_repair_cost=cmd.estimated_repair_cost,
            damaged_items=cmd.damaged_items,
            is_total_loss=cmd.is_total_loss,
            evidence_urls=cmd.evidence_urls,
        )

        claim.attach_assessment(assessment)

        # Consulta birô antifraude externo através de interface (Port)
        fraud_score = self._fraud_gateway.evaluate_risk(claim)

        # Regulação pura no Domain Service
        decision = self._evaluator_service.evaluate(
            policy=policy,
            claim=claim,
            assessment=assessment,
            external_fraud_score=fraud_score,
        )

        # Atualiza a entidade de domínio
        claim.apply_decision(decision)
        self._claim_repo.save(claim)

        # Notifica o cliente
        resumo = f"Sinistro #{claim.claim_id}: {decision.status.value}. {decision.justification}"
        self._notification_gateway.notify_insured(claim.insured_name, resumo)

        return SettleClaimResponse(
            claim_id=claim.claim_id,
            status=decision.status.value,
            approved=decision.approved,
            gross_loss=decision.gross_loss,
            deductible_applied=decision.deductible_applied,
            payable_amount=decision.payable_amount,
            justification=decision.justification,
        )
