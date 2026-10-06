"""Message Transformer: Conversão para o Modelo Canônico de Telecom e MML de Rede."""

from typing import Dict, Any, Tuple
from canonical.provisioning_models import (
    SubscriberInfo,
    LineDetails,
    CanonicalProvisioningRequest,
)


class TelecomMessageTransformer:
    @staticmethod
    def crm_to_canonical(crm_payload: Dict[str, Any]) -> CanonicalProvisioningRequest:
        sub_data = crm_payload.get("subscriber", {})
        line_data = crm_payload.get("line", {})

        return CanonicalProvisioningRequest(
            order_id=crm_payload.get("order_id", ""),
            subscriber=SubscriberInfo(
                name=sub_data.get("full_name", ""),
                cpf=sub_data.get("cpf", ""),
                email=sub_data.get("email", ""),
            ),
            line=LineDetails(
                msisdn=line_data.get("phone_number", ""),
                iccid_sim=line_data.get("sim_card_iccid", ""),
                plan_code=line_data.get("plan_id", ""),
                monthly_fee=float(line_data.get("monthly_price", 0.0)),
            ),
        )

    @staticmethod
    def canonical_to_hlr_mml(req: CanonicalProvisioningRequest) -> str:
        # Formato MML telefônico padrão: ADD-SUB:MSISDN=...,PROFILE=...
        return f"ADD-SUB:MSISDN={req.line.msisdn},PROFILE={req.line.plan_code}"

    @staticmethod
    def parse_hlr_response(raw_resp: str) -> Tuple[bool, str]:
        # Formato: "RETCODE=0,DESC=...,ROUTING=HLR_NODE_SP_7777"
        if not raw_resp.startswith("RETCODE=0"):
            return False, ""
        parts = dict(p.split("=") for p in raw_resp.split(",") if "=" in p)
        return True, parts.get("ROUTING", "")

    @staticmethod
    def canonical_to_billing_payload(req: CanonicalProvisioningRequest) -> Dict[str, Any]:
        return {
            "cpf": req.subscriber.cpf,
            "msisdn": req.line.msisdn,
            "plan_code": req.line.plan_code,
            "monthly_fee": req.line.monthly_fee,
        }
