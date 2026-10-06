"""Ponto de Entrada e Facade do Módulo Compliance."""

from modules.compliance.public_contracts import (
    IComplianceModule,
    ComplianceCheckRequestDto,
    ComplianceDecisionDto,
)
from modules.compliance.internal.compliance_internal import _InternalComplianceRepository


class ComplianceModule(IComplianceModule):
    """Facade do módulo Compliance."""
    def __init__(self) -> None:
        self._repo = _InternalComplianceRepository()

    def blacklist_pix_key(self, pix_key: str) -> None:
        self._repo.add_blacklisted_key(pix_key)

    def evaluate_transfer(self, req: ComplianceCheckRequestDto) -> ComplianceDecisionDto:
        # 1. Checagem de Lista Restritiva / Fraude Conhecida
        if self._repo.is_blacklisted(req.destination_pix_key):
            return ComplianceDecisionDto(
                is_approved=False,
                requires_manual_review=False,
                risk_score=1.0,
                reason="Bloqueio Cautelar: Chave PIX destinatária consta na lista de sanções/contas fraudulentas.",
            )

        # 2. Monitoramento Regulatório de Grande Porte (COAF / BACEN)
        # Transações acima de R$ 50.000 são retidas para quarentena e análise humana
        if req.amount >= 50_000.0:
            return ComplianceDecisionDto(
                is_approved=False,
                requires_manual_review=True,
                risk_score=0.85,
                reason="Transferência de alto valor retida para compliance regulatório COAF (Prevenção à Lavagem de Dinheiro).",
            )

        # Transação segura
        return ComplianceDecisionDto(
            is_approved=True,
            requires_manual_review=False,
            risk_score=0.05,
            reason="Transação liberada pelas regras de conformidade e limites operacionais.",
        )
