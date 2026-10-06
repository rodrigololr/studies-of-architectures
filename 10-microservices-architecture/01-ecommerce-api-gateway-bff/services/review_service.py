"""Review Microservice - Responsável exclusivo por avaliações e comentários de clientes."""

from typing import Dict, Any, Optional, List


class ReviewService:
    """Microsserviço de Avaliações com banco próprio (Database-per-Service)."""

    def __init__(self) -> None:
        self._db: Dict[str, Dict[str, Any]] = {
            "PROD-001": {
                "product_id": "PROD-001",
                "average_rating": 4.8,
                "total_reviews": 128,
                "recent_comments": [
                    {"author": "Ana Paula", "stars": 5, "comment": "A câmera com IA é sensacional!"},
                    {"author": "Lucas Moura", "stars": 5, "comment": "Bateria dura mais de um dia inteiro com folga."},
                    {"author": "Juliana R.", "stars": 4, "comment": "Excelente aparelho, porém um pouco pesado na mão."},
                ],
            },
            "PROD-002": {
                "product_id": "PROD-002",
                "average_rating": 4.6,
                "total_reviews": 34,
                "recent_comments": [
                    {"author": "Rodrigo S.", "stars": 5, "comment": "Tela OLED mais linda que já vi em um notebook."},
                    {"author": "Felipe K.", "stars": 4, "comment": "Esquenta um pouco em render 3D pesado, mas voa."},
                ],
            },
        }

    def get_reviews_by_product_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        return self._db.get(product_id)
