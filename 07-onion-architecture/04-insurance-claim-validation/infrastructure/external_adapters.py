"""Adaptadores de infraestrutura para serviços externos (Ring 4)."""

from domain.model.claim import Claim
from application.interfaces import IFraudDetectionGateway, INotificationGateway


class MockFraudDetectionBureauGateway(IFraudDetectionGateway):
    """Adaptador de infraestrutura que simula análise de birô antifraude (ex: Serasa/Clearsale)."""
    def __init__(self, high_risk_claim_ids: list = None) -> None:
        self._high_risk_ids = high_risk_claim_ids or []

    def evaluate_risk(self, claim: Claim) -> float:
        # Se cadastrado como suspeito na simulação, pontua 0.88 (alto risco)
        if claim.claim_id in self._high_risk_ids or "GOLPE" in claim.description.upper():
            return 0.88
        return 0.05  # Risco normal/baixo


class MockNotificationGateway(INotificationGateway):
    """Adaptador para envio de notificações por SMS e Push."""
    def __init__(self) -> None:
        self.sent_notifications = []

    def notify_insured(self, insured_name: str, message: str) -> None:
        log_entry = f"[SMS/Notificação para '{insured_name}']: {message}"
        self.sent_notifications.append(log_entry)
