"""Serviço Autoritativo do Registro Civil das Pessoas Naturais (Cartórios)."""

from typing import Dict, Any, Optional


class CartorioCivilService:
    """Base mestre de certidões de nascimento, casamento e óbito."""

    def __init__(self) -> None:
        self._certidao_db: Dict[str, Dict[str, Any]] = {
            "11122233344": {
                "matricula": "123456.01.55.2018.1.00123.456.0001234-55",
                "estado_civil": "CASADO(A)",
                "municipio": "São Paulo - SP",
            },
            "55566677788": {
                "matricula": "987654.01.55.2021.1.00045.789.0009876-12",
                "estado_civil": "SOLTEIRO(A)",
                "municipio": "Campinas - SP",
            },
            "99988877766": {
                "matricula": "333222.01.55.2010.1.00987.654.0003332-99",
                "estado_civil": "DIVORCIADO(A)",
                "municipio": "Belo Horizonte - MG",
            },
        }

    def consultar_registro_civil(self, cpf: str) -> Optional[Dict[str, Any]]:
        clean_cpf = cpf.replace(".", "").replace("-", "").strip()
        return self._certidao_db.get(clean_cpf)
