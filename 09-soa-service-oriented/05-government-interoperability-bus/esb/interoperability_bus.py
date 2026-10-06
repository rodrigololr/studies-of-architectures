"""Enterprise Service Bus (ESB): Barramento de Interoperabilidade Governamental."""

from typing import Optional, List
from canonical.citizen_models import (
    FiscalStatus,
    LicenseStatus,
    MaritalStatus,
    TaxIdentificationRecord,
    DriverLicenseRecord,
    CivilRegistryRecord,
    UnifiedCitizenRecord,
)
from government_organs.receita_federal_service import ReceitaFederalService
from government_organs.detran_service import DetranService
from government_organs.cartorio_civil_service import CartorioCivilService
from esb.service_registry import ServiceRegistry
from esb.audit_logger import AuditLogger


class GovernmentInteroperabilityBus:
    """Barramento SOA federado de dados públicos do Cidadão."""

    def __init__(
        self,
        receita_service: ReceitaFederalService,
        detran_service: DetranService,
        cartorio_service: CartorioCivilService,
        registry: ServiceRegistry,
        audit_logger: AuditLogger,
    ) -> None:
        self._receita = receita_service
        self._detran = detran_service
        self._cartorio = cartorio_service
        self._registry = registry
        self._audit = audit_logger

    def consult_citizen_dossier(
        self, consumer_id: str, cpf: str
    ) -> Optional[UnifiedCitizenRecord]:
        """Consulta federada e unificação dos dados do cidadão conforme autorização do consumidor."""

        # 1. Validação de autorização no Serviço Primário (Receita Federal)
        if not self._registry.is_authorized(consumer_id, "SVC_RECEITA_CPF"):
            self._audit.record_access(
                consumer_id=consumer_id,
                cpf=cpf,
                services=["SVC_RECEITA_CPF"],
                granted=False,
                details="Consumidor sem autorização de leitura da base primária de CPF",
            )
            raise PermissionError(f"Acesso negado para o órgão '{consumer_id}' na base de CPF.")

        raw_receita = self._receita.consultar_cpf(cpf)
        if not raw_receita:
            self._audit.record_access(
                consumer_id=consumer_id,
                cpf=cpf,
                services=["SVC_RECEITA_CPF"],
                granted=True,
                details="CPF não encontrado na base da Receita Federal",
            )
            return None

        # 2. Construção do registro primário canônico
        tax_info = TaxIdentificationRecord(
            cpf=raw_receita["cpf"],
            full_name=raw_receita["nome_completo"],
            birth_date=raw_receita["data_nascimento"],
            fiscal_status=FiscalStatus(raw_receita["situacao_cadastral"]),
        )

        accessed_services = ["SVC_RECEITA_CPF"]
        restrictions: List[str] = []

        # 3. Consulta condicional ao DETRAN
        driver_info: Optional[DriverLicenseRecord] = None
        if self._registry.is_authorized(consumer_id, "SVC_DETRAN_CNH"):
            accessed_services.append("SVC_DETRAN_CNH")
            raw_cnh = self._detran.consultar_cnh_por_cpf(cpf)
            if raw_cnh:
                driver_info = DriverLicenseRecord(
                    cnh_number=raw_cnh["numero_cnh"],
                    category=raw_cnh["categoria"],
                    points=raw_cnh["pontos"],
                    license_status=LicenseStatus(raw_cnh["status_cnh"]),
                    valid_until=raw_cnh["data_validade"],
                )
        else:
            restrictions.append("DETRAN_CNH_OMITTED_DUE_TO_CLEARANCE")

        # 4. Consulta condicional ao Cartório Civil
        civil_info: Optional[CivilRegistryRecord] = None
        if self._registry.is_authorized(consumer_id, "SVC_CARTORIO_CIVIL"):
            accessed_services.append("SVC_CARTORIO_CIVIL")
            raw_civil = self._cartorio.consultar_registro_civil(cpf)
            if raw_civil:
                civil_info = CivilRegistryRecord(
                    certidao_matricula=raw_civil["matricula"],
                    marital_status=MaritalStatus(raw_civil["estado_civil"]),
                    cartorio_municipio=raw_civil["municipio"],
                )
        else:
            restrictions.append("CARTORIO_CIVIL_OMITTED_DUE_TO_CLEARANCE")

        # 5. Registro na Trilha de Auditoria LGPD
        self._audit.record_access(
            consumer_id=consumer_id,
            cpf=cpf,
            services=accessed_services,
            granted=True,
            details=f"Dossiê gerado com restrições: {restrictions if restrictions else 'NENHUMA'}",
        )

        # 6. Retorno do Modelo Canônico Unificado
        return UnifiedCitizenRecord(
            cpf=tax_info.cpf,
            tax_info=tax_info,
            driver_info=driver_info,
            civil_info=civil_info,
            access_restrictions_applied=restrictions if restrictions else None,
        )
