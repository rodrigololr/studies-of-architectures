"""Serviço Autoritativo do DETRAN (Departamento Estadual de Trânsito - CNH)."""

from typing import Dict, Any, Optional


class DetranService:
    """Base mestre de habilitação e trânsito (CNH)."""

    def __init__(self) -> None:
        self._cnh_db: Dict[str, Dict[str, Any]] = {
            "11122233344": {
                "numero_cnh": "04928172930",
                "categoria": "AB",
                "pontos": 4,
                "status_cnh": "ATIVA",
                "data_validade": "2029-08-10",
            },
            "55566677788": {
                "numero_cnh": "08192837461",
                "categoria": "B",
                "pontos": 22,
                "status_cnh": "SUSPENSA",
                "data_validade": "2027-02-15",
            },
            # Roberto não possui CNH registrada
        }

    def consultar_cnh_por_cpf(self, cpf: str) -> Optional[Dict[str, Any]]:
        clean_cpf = cpf.replace(".", "").replace("-", "").strip()
        return self._cnh_db.get(clean_cpf)
