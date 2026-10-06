"""
loan_application_api_controller.py - Adaptador Primário HTTP REST para Propostas de Empréstimo.
"""

from __future__ import annotations
from typing import Dict, Any, Tuple
from domain.models import Applicant, LoanProposal
from domain.exceptions import CreditDomainException
from ports.driver import UnderwriteCreditProposalUseCasePort, GetCreditDossierUseCasePort


class LoanApplicationApiController:
    def __init__(
        self,
        underwrite_use_case: UnderwriteCreditProposalUseCasePort,
        dossier_use_case: GetCreditDossierUseCasePort,
    ) -> None:
        self.underwrite_use_case = underwrite_use_case
        self.dossier_use_case = dossier_use_case

    def handle_submit_proposal(self, payload: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
        try:
            applicant_data = payload.get("applicant", {})
            applicant = Applicant(
                cpf=applicant_data.get("cpf", ""),
                full_name=applicant_data.get("name", ""),
                monthly_income=float(applicant_data.get("income", 0.0)),
                birth_date=applicant_data.get("birth_date", "1990-01-01"),
            )

            proposal = LoanProposal(
                proposal_id=payload.get("proposal_id", ""),
                applicant=applicant,
                requested_amount=float(payload.get("amount", 0.0)),
                installments_count=int(payload.get("installments", 12)),
            )

            result = self.underwrite_use_case.evaluate(proposal)

            return 200, {
                "success": True,
                "proposal_id": result.proposal_id,
                "decision": result.decision.value,
                "risk_rating": result.risk_rating.value,
                "approved_amount": result.approved_amount,
                "monthly_installment": result.monthly_installment,
                "annual_interest_rate": result.annual_interest_rate,
                "reasons": result.reasons,
                "analyzed_at": result.analyzed_at.isoformat(),
            }

        except CreditDomainException as dom_err:
            return 422, {
                "success": False,
                "error": dom_err.__class__.__name__,
                "detail": str(dom_err),
            }
        except Exception as ex:
            return 500, {
                "success": False,
                "error": "InternalServerError",
                "detail": str(ex),
            }
