"""Downstream ML Scoring Microservice (Simulador de serviço intensivo e instável)."""

from typing import List, Dict, Any


class MachineLearningScoringService:
    """Microsserviço de Machine Learning para personalização em tempo real.
    
    Pode sofrer degradação ou quedas de cluster sob alta carga.
    """

    def __init__(self) -> None:
        self._is_healthy: bool = True

    def set_health(self, is_healthy: bool) -> None:
        self._is_healthy = is_healthy

    def compute_personalized_recommendations(
        self, user_id: str
    ) -> List[Dict[str, Any]]:
        if not self._is_healthy:
            raise TimeoutError(
                "Timeout de rede (504 Gateway Timeout): Cluster GPU de Machine Learning inacessível."
            )

        # Retorno normal e personalizado
        return [
            {"title": "Interestelar 4K", "score": 0.98, "source": "ML_REALTIME_AI"},
            {"title": "Oppenheimer", "score": 0.94, "source": "ML_REALTIME_AI"},
            {"title": "Blade Runner 2049", "score": 0.91, "source": "ML_REALTIME_AI"},
        ]
