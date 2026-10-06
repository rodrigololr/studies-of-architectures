"""Enterprise Service Bus (ESB): Orquestrador de Provisionamento de Telecom."""

from typing import Dict, Any
from canonical.provisioning_models import CanonicalProvisioningResponse
from esb.service_registry import TelecomServiceRegistry
from esb.message_transformer import TelecomMessageTransformer
from services.sim_inventory_service import SimCardInventoryService
from services.network_hlr_service import NetworkHlrService
from services.billing_platform_service import BillingPlatformService


class TelecomProvisioningESB:
    def __init__(self, registry: TelecomServiceRegistry) -> None:
        self._registry = registry
        self._transformer = TelecomMessageTransformer()

    def process_activation(self, crm_request: Dict[str, Any]) -> CanonicalProvisioningResponse:
        # 1. Lookup de serviços no Registry
        inv_meta = self._registry.lookup("SimCardInventoryService")
        hlr_meta = self._registry.lookup("NetworkHlrService")
        bill_meta = self._registry.lookup("BillingPlatformService")

        if not inv_meta or not hlr_meta or not bill_meta:
            return CanonicalProvisioningResponse(
                order_id=crm_request.get("order_id", ""),
                msisdn=crm_request.get("line", {}).get("phone_number", ""),
                status="ESB_SERVICES_UNAVAILABLE",
                hlr_routing_code=None,
                billing_cycle_day=None,
                message="Falha de Governança SOA: Serviços participantes não disponíveis no catálogo.",
            )

        inventory_svc: SimCardInventoryService = inv_meta.instance
        hlr_svc: NetworkHlrService = hlr_meta.instance
        billing_svc: BillingPlatformService = bill_meta.instance

        # 2. Converte CRM -> Canonical Data Model (CDM)
        canonical = self._transformer.crm_to_canonical(crm_request)

        # 3. Passo 1: Alocação e validação no Inventário de Chips
        sim_allocated = inventory_svc.validate_and_allocate(
            iccid=canonical.line.iccid_sim,
            msisdn=canonical.line.msisdn,
        )
        if not sim_allocated:
            return CanonicalProvisioningResponse(
                order_id=canonical.order_id,
                msisdn=canonical.line.msisdn,
                status="REJECTED_INVENTORY",
                hlr_routing_code=None,
                billing_cycle_day=None,
                message=f"Chip SIM '{canonical.line.iccid_sim}' inválido, extraviado ou já ativado.",
            )

        # 4. Passo 2: Provisionamento na Rede Celular (HLR / Antenas)
        mml_cmd = self._transformer.canonical_to_hlr_mml(canonical)
        hlr_resp = hlr_svc.execute_mml_command(mml_cmd)
        hlr_ok, routing_node = self._transformer.parse_hlr_response(hlr_resp)

        if not hlr_ok:
            # Desfaz a alocação do SIM
            inventory_svc.release_sim(canonical.line.iccid_sim)
            return CanonicalProvisioningResponse(
                order_id=canonical.order_id,
                msisdn=canonical.line.msisdn,
                status="HLR_NETWORK_ERROR",
                hlr_routing_code=None,
                billing_cycle_day=None,
                message=f"Falha de ativação na rede core de rádio (HLR): {hlr_resp}",
            )

        # 5. Passo 3: Ativação na Plataforma de Faturamento (Billing)
        billing_payload = self._transformer.canonical_to_billing_payload(canonical)
        bill_resp = billing_svc.activate_account(billing_payload)

        # 6. Compensação caso o faturamento falhe (Rollback Transacional no ESB)
        if not bill_resp["success"]:
            # Rollback: Desprovisiona na rede HLR e libera o chip físico
            hlr_svc.execute_mml_command(f"DEL-SUB:MSISDN={canonical.line.msisdn}")
            inventory_svc.release_sim(canonical.line.iccid_sim)

            return CanonicalProvisioningResponse(
                order_id=canonical.order_id,
                msisdn=canonical.line.msisdn,
                status="COMPENSATED_FAILED",
                hlr_routing_code=None,
                billing_cycle_day=None,
                message=f"Ativação cancelada por rejeição de faturamento ({bill_resp['error']}). Rede HLR e Chip compensados.",
            )

        # 7. Sucesso integral
        return CanonicalProvisioningResponse(
            order_id=canonical.order_id,
            msisdn=canonical.line.msisdn,
            status="ACTIVATED",
            hlr_routing_code=routing_node,
            billing_cycle_day=bill_resp["billing_cycle_day"],
            message=f"Linha ativada com sucesso em todas as camadas corporativas de telecomunicações.",
        )
