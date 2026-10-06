"""Domain Service: Avaliação técnica, regulação e liquidação de sinistros."""

from domain.model.policy import Policy
from domain.model.claim import Claim, ClaimStatus, ClaimSettlementDecision
from domain.model.damage_assessment import DamageAssessment
from domain.model.exceptions import CoverageExcludedException


class ClaimEvaluatorDomainService:
    """Serviço de Domínio puro (Ring 2 da Onion Architecture).
    
    Encapsula as regras de liquidação que dependem da interação de múltiplas
    entidades e laudos periciais sem depender de bancos de dados ou APIs externas.
    """

    DISCREPANCY_FRAUD_RATIO_THRESHOLD = 3.0  # Reclamar 3x mais que o laudo gera alerta

    def evaluate(
        self,
        policy: Policy,
        claim: Claim,
        assessment: DamageAssessment,
        external_fraud_score: float = 0.0,
    ) -> ClaimSettlementDecision:
        """Avalia e decide a liquidação do sinistro conforme regras contratuais e periciais."""
        # 1. Validação de vigência temporal e adimplência da apólice
        policy.validate_eligibility_for_event(claim.occurrence_date)

        # 2. Verificação de causas expressamente excluídas
        if policy.is_cause_excluded(assessment.loss_cause) or assessment.is_natural_wear():
            return ClaimSettlementDecision(
                approved=False,
                status=ClaimStatus.REJECTED,
                gross_loss=assessment.estimated_repair_cost,
                deductible_applied=0.0,
                payable_amount=0.0,
                justification=f"Causa '{assessment.loss_cause}' não possui cobertura (risco expressamente excluído na apólice).",
            )

        # 3. Análise de risco e suspeita de fraude
        is_discrepant = (
            assessment.estimated_repair_cost > 0
            and (claim.claimed_amount / assessment.estimated_repair_cost) >= self.DISCREPANCY_FRAUD_RATIO_THRESHOLD
        )
        is_high_fraud_score = external_fraud_score >= 0.80

        if is_discrepant or is_high_fraud_score:
            motivo = []
            if is_discrepant:
                motivo.append(f"discrepância severa entre valor reclamado (R${claim.claimed_amount:.2f}) e periciado (R${assessment.estimated_repair_cost:.2f})")
            if is_high_fraud_score:
                motivo.append(f"score de risco elevado ({external_fraud_score*100:.0f}%)")
            return ClaimSettlementDecision(
                approved=False,
                status=ClaimStatus.FRAUD_SUSPECTED,
                gross_loss=assessment.estimated_repair_cost,
                deductible_applied=0.0,
                payable_amount=0.0,
                justification=f"Sinistro encaminhado para investigação especial: {', '.join(motivo)}.",
            )

        # 4. Cálculo da indenização financeira
        gross_covered_loss = min(assessment.estimated_repair_cost, policy.coverage_limit)
        net_payable = gross_covered_loss - policy.deductible

        if net_payable <= 0.0:
            return ClaimSettlementDecision(
                approved=False,
                status=ClaimStatus.REJECTED,
                gross_loss=assessment.estimated_repair_cost,
                deductible_applied=policy.deductible,
                payable_amount=0.0,
                justification=f"Prejuízo apurado (R${gross_covered_loss:.2f}) não atinge o valor da franquia (R${policy.deductible:.2f}).",
            )

        justification_msg = "Sinistro aprovado para pagamento de indenização integral/parcial."
        if assessment.estimated_repair_cost > policy.coverage_limit:
            justification_msg += f" (Prejuízo total R${assessment.estimated_repair_cost:.2f} limitado ao teto da apólice R${policy.coverage_limit:.2f})."

        return ClaimSettlementDecision(
            approved=True,
            status=ClaimStatus.APPROVED,
            gross_loss=assessment.estimated_repair_cost,
            deductible_applied=policy.deductible,
            payable_amount=round(net_payable, 2),
            justification=justification_msg,
        )
