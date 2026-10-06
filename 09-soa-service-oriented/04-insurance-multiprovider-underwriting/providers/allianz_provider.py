"""Provedor Allianz: Serviço Moderno REST / JSON."""

import uuid
from typing import Dict, Any


class AllianzRestService:
    """Simulador de Microserviço REST da Allianz.
    
    Recebe e devolve dicionários/JSON estruturados.
    """

    def quote_policy_rest(self, json_data: Dict[str, Any]) -> Dict[str, Any]:
        vehicle = json_data.get("asset", {})
        driver = json_data.get("risk_profile", {})
        coverage = json_data.get("selected_tier", "STANDARD")

        ano = int(vehicle.get("manufacturing_year", 2020))
        valor = float(vehicle.get("market_valuation", 0.0))
        driver_age = int(driver.get("driver_age", 30))

        # Regra de Subscrição da Allianz: Não aceita veículos com mais de 15 anos
        current_year = 2026
        if (current_year - ano) > 15:
            return {
                "outcome": "DECLINED",
                "decline_reason": f"Veiculo com ano {ano} excede o limite maximo de 15 anos de fabricacao",
            }

        # Cálculo do Prêmio Allianz
        taxa = 0.040
        if coverage == "BASIC":
            taxa = 0.028
        elif coverage == "COMPREHENSIVE":
            taxa = 0.052

        # Motoristas experientes (> 30 anos) ganham leve bonificação
        if driver_age >= 30:
            taxa *= 0.95

        premio = round(valor * taxa, 2)
        franquia = 3500.00  # Franquia fixa contratual Allianz
        quote_ref = f"ALZ-{uuid.uuid4().hex[:8].upper()}"

        return {
            "outcome": "ACCEPTED",
            "quote_reference": quote_ref,
            "cost_breakdown": {
                "annual_premium": premio,
                "deductible_amount": franquia,
            },
            "tier": coverage,
        }
