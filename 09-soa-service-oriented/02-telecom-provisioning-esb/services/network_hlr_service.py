"""Serviço Core de Rede Celular: Home Location Register (HLR / HSS).

Utiliza formato de comandos legados MML (Man-Machine Language) amplamente
empregado em centrais telefônicas Ericsson, Huawei e Nokia.
"""

from typing import Dict


class NetworkHlrService:
    def __init__(self) -> None:
        self._active_network_subscribers: Dict[str, str] = {}  # msisdn -> imsi_routing

    def execute_mml_command(self, mml_string: str) -> str:
        # Exemplo: "ADD-SUB:MSISDN=5511988887777,PROFILE=4G5G_VOICE"
        if mml_string.startswith("ADD-SUB:"):
            params = dict(item.split("=") for item in mml_string.replace("ADD-SUB:", "").split(","))
            msisdn = params.get("MSISDN", "")
            routing_key = f"HLR_NODE_SP_{msisdn[-4:]}"
            self._active_network_subscribers[msisdn] = routing_key
            return f"RETCODE=0,DESC=SUBSCRIBER_PROVISIONED_SUCCESSFULLY,ROUTING={routing_key}"

        # Exemplo: "DEL-SUB:MSISDN=5511988887777"
        if mml_string.startswith("DEL-SUB:"):
            params = dict(item.split("=") for item in mml_string.replace("DEL-SUB:", "").split(","))
            msisdn = params.get("MSISDN", "")
            if msisdn in self._active_network_subscribers:
                del self._active_network_subscribers[msisdn]
                return "RETCODE=0,DESC=SUBSCRIBER_DEPROVISIONED_SUCCESSFULLY"
            return "RETCODE=104,DESC=SUBSCRIBER_NOT_FOUND"

        return "RETCODE=999,DESC=SYNTAX_ERROR"
