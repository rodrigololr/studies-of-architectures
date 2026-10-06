"""
bank_teller_console_adapter.py - Adaptador Primário de Terminal do Gerente de Agência.
"""

from __future__ import annotations
from domain.models import Applicant, LoanProposal
from ports.driver import UnderwriteCreditProposalUseCasePort


class BankTellerConsoleAdapter:
    def __init__(self, underwrite_use_case: UnderwriteCreditProposalUseCasePort, branch_id: str) -> None:
        self.underwrite_use_case = underwrite_use_case
        self.branch_id = branch_id

    def process_counter_proposal(
        self,
        cpf: str,
        name: str,
        income: float,
        amount: float,
        installments: int,
    ) -> str:
        applicant = Applicant(cpf=cpf, full_name=name, monthly_income=income, birth_date="1985-05-10")
        proposal = LoanProposal(
            proposal_id=f"AG-{self.branch_id}-PROP-1",
            applicant=applicant,
            requested_amount=amount,
            installments_count=installments,
        )
        res = self.underwrite_use_case.evaluate(proposal)
        if res.decision.value == "APPROVED":
            return (
                f"[Agência {self.branch_id}] Proposta {res.proposal_id} APROVADA! "
                f"Rating: {res.risk_rating.value} | Parcela: R$ {res.monthly_installment:.2f} ({installments}x) | Taxa: {res.annual_interest_rate}% a.a."
            )
        else:
            reasons_str = "; ".join(res.reasons)
            return f"[Agência {self.branch_id}] Proposta {res.proposal_id} RECUSADA. Motivos: {reasons_str}"
