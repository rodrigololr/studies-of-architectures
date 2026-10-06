"""Recommendation Microservice: Consome ML protegido por Circuit Breaker com Fallback."""

from typing import Dict, Any, List
from resilience.circuit_breaker import CircuitBreaker, CircuitBreakerOpenException
from services.ml_scoring_service import MachineLearningScoringService


class RecommendationService:
    """Microsserviço de Vitrine de Recomendações com Degradação Graciosa."""

    def __init__(
        self,
        ml_service: MachineLearningScoringService,
        circuit_breaker: CircuitBreaker,
    ) -> None:
        self._ml = ml_service
        self._cb = circuit_breaker

        # Fallback Estático em Cache (Top Mais Assistidos Globais)
        self._cached_fallback_titles: List[Dict[str, Any]] = [
            {"title": "Breaking Bad (Top 1 Brasil)", "score": 1.0, "source": "STATIC_CACHE_FALLBACK"},
            {"title": "Stranger Things", "score": 0.99, "source": "STATIC_CACHE_FALLBACK"},
            {"title": "The Last of Us", "score": 0.98, "source": "STATIC_CACHE_FALLBACK"},
        ]

    def get_recommendations_for_user(self, user_id: str) -> Dict[str, Any]:
        """Tenta consultar a IA em tempo real; se o circuito abrir ou falhar, ativa fallback."""
        try:
            items = self._cb.execute(self._ml.compute_personalized_recommendations, user_id)
            return {
                "user_id": user_id,
                "status": "SUCCESS",
                "circuit_state": self._cb.state.value,
                "mode": "REALTIME_PERSONALIZED",
                "recommendations": items,
            }
        except (CircuitBreakerOpenException, Exception) as exc:
            # Fallback Gracioso: O usuário nunca vê tela de erro 500
            return {
                "user_id": user_id,
                "status": "DEGRADED",
                "circuit_state": self._cb.state.value,
                "mode": "FALLBACK_DEGRADED",
                "reason": str(exc),
                "recommendations": self._cached_fallback_titles,
            }
