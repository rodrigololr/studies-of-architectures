"""Serviço de Faturamento e Billing de Telecomunicações (Amdocs / Netcracker Simulator)."""

import uuid
from typing import Dict, Any


class BillingPlatformService:
    def __init__(self) -> None:
        self._accounts: Dict[str, Dict[str, Any]] = {}

    def activate_account(self, contract_data: Dict[str, Any]) -> Dict[str, Any]:
        cpf = contract_data.get("cpf", "")
        msisdn = contract_data.get("msisdn", "")
        plan = contract_data.get("plan_code", "")

        # Simulação de erro se CPF for marcado como inadimplente histórico
        if "INADIMPLENTE" in cpf:
            return {
                "success": False,
                "account_id": None,
                "error": "Assinante possui débitos pendentes em cadastro de inadimplentes.",
            }

        acc_id = f"BILL_{uuid.uuid4().hex[:8].upper()}"
        self._accounts[msisdn] = {
            "account_id": acc_id,
            "cpf": cpf,
            "plan": plan,
            "billing_cycle_day": 15,
        }
        return {
            "success": True,
            "account_id": acc_id,
            "billing_cycle_day": 15,
            "error": None,
        }
