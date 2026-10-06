"""Modelos de avaliação de danos (Damage Assessment)."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass(frozen=True)
class DamageAssessment:
    """Relatório técnico pericial de vistoria de danos (Value Object imutável)."""
    assessor_id: str
    assessment_date: datetime
    loss_cause: str  # ex: "COLISAO", "INCENDIO", "ROUBO", "ALAGAMENTO", "DESGASTE_NATURAL"
    estimated_repair_cost: float
    damaged_items: List[str] = field(default_factory=list)
    is_total_loss: bool = False
    evidence_urls: List[str] = field(default_factory=list)

    def is_natural_wear(self) -> bool:
        """Verifica se o dano decorre de desgaste natural/falta de manutenção."""
        return self.loss_cause.upper() in ["DESGASTE_NATURAL", "FALTA_MANUTENCAO", "DEFEITO_FABRICACAO"]
