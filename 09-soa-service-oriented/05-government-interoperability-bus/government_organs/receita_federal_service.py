"""Serviço Autoritativo da Receita Federal do Brasil (Cadastro de Pessoas Físicas - CPF)."""

from typing import Dict, Any, Optional


class ReceitaFederalService:
    """Base de dados mestre da União para identificação fiscal e dados vitais primários."""

    def __init__(self) -> None:
        self._database: Dict[str, Dict[str, Any]] = {
            "11122233344": {
                "cpf": "11122233344",
                "nome_completo": "Carlos Eduardo da Silva",
                "data_nascimento": "1988-05-14",
                "situacao_cadastral": "REGULAR",
            },
            "55566677788": {
                "cpf": "55566677788",
                "nome_completo": "Mariana Souza Oliveira",
                "data_nascimento": "1994-11-20",
                "situacao_cadastral": "PENDENTE_REGULARIZACAO",
            },
            "99988877766": {
                "cpf": "99988877766",
                "nome_completo": "Roberto Albuquerque Mendes",
                "data_nascimento": "1972-03-01",
                "situacao_cadastral": "SUSPENSO",
            },
        }

    def consultar_cpf(self, cpf: str) -> Optional[Dict[str, Any]]:
        clean_cpf = cpf.replace(".", "").replace("-", "").strip()
        return self._database.get(clean_cpf)
