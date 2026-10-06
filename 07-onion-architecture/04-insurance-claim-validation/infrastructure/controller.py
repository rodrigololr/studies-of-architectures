"""Controlador de apresentação (Ring 4 - Infrastructure)."""

from typing import Dict, Any
from application.claim_service import ClaimApplicationService
from application.dtos import SubmitClaimCommand, AssessClaimCommand
from domain.model.exceptions import InsuranceDomainException


class InsuranceClaimsController:
    """Controlador que adapta requisições HTTP / CLI para comandos da aplicação."""
    def __init__(self, claim_service: ClaimApplicationService) -> None:
        self._claim_service = claim_service

    def post_submit_claim(self, cmd: SubmitClaimCommand) -> Dict[str, Any]:
        try:
            res = self._claim_service.submit_claim(cmd)
            return {
                "http_status": 201,
                "data": {
                    "claim_id": res.claim_id,
                    "status": res.status,
                    "message": res.message,
                }
            }
        except InsuranceDomainException as e:
            return {
                "http_status": 400,
                "data": {"status": "REJECTED", "error": str(e)}
            }

    def post_assess_claim(self, cmd: AssessClaimCommand) -> Dict[str, Any]:
        try:
            res = self._claim_service.assess_and_settle_claim(cmd)
            return {
                "http_status": 200,
                "data": {
                    "claim_id": res.claim_id,
                    "status": res.status,
                    "approved": res.approved,
                    "gross_loss": f"R$ {res.gross_loss:,.2f}",
                    "deductible_applied": f"R$ {res.deductible_applied:,.2f}",
                    "payable_amount": f"R$ {res.payable_amount:,.2f}",
                    "justification": res.justification,
                }
            }
        except InsuranceDomainException as e:
            return {
                "http_status": 400,
                "data": {"status": "ERROR", "error": str(e)}
            }
