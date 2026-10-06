"""Demonstração de SOA: Barramento de Interoperabilidade Governamental (e-PING / X-Road).

Cenários demonstrados:
1. Ministério Público (Acesso Total): Dossiê unificado completo (Receita, DETRAN e Cartório).
2. Polícia Rodoviária Federal (Segurança de Trânsito): Acesso a Receita e DETRAN, Cartório omitido.
3. Prefeitura Municipal (Acesso Básico Cidadão): Apenas Receita, dados de trânsito e cartório omitidos por sigilo.
4. Órgão / Entidade não autorizada: Recusa formal com bloqueio no barramento e registro na auditoria.
5. Verificação da Trilha de Auditoria e Conformidade LGPD no barramento.
"""

import sys
from pathlib import Path

# Garante resolução de imports absolutos
sys.path.insert(0, str(Path(__file__).parent))

from government_organs.receita_federal_service import ReceitaFederalService
from government_organs.detran_service import DetranService
from government_organs.cartorio_civil_service import CartorioCivilService
from esb.service_registry import ServiceRegistry
from esb.audit_logger import AuditLogger
from esb.interoperability_bus import GovernmentInteroperabilityBus


def print_separator(title: str) -> None:
    print(f"\n{'='*75}\n>>> {title}\n{'='*75}")


def main() -> None:
    print("Inicializando Barramento SOA de Interoperabilidade Governamental...")

    # Inicialização dos Órgãos Autoritativos Autônomos
    receita_svc = ReceitaFederalService()
    detran_svc = DetranService()
    cartorio_svc = CartorioCivilService()

    # Catálogo e Governança
    registry = ServiceRegistry()
    audit_logger = AuditLogger()

    # Barramento de Interoperabilidade (ESB)
    bus = GovernmentInteroperabilityBus(
        receita_service=receita_svc,
        detran_service=detran_svc,
        cartorio_service=cartorio_svc,
        registry=registry,
        audit_logger=audit_logger,
    )

    # -------------------------------------------------------------------------
    # Cenário 1: Ministério Público (Acesso Total)
    # -------------------------------------------------------------------------
    print_separator("Cenário 1: Ministério Público consultando Dossiê Completo (CPF 111.222.333-44)")
    dossier1 = bus.consult_citizen_dossier("MINISTERIO_PUBLICO", "11122233344")
    assert dossier1 is not None
    print(f"Cidadão: {dossier1.tax_info.full_name} | Situação Fiscal: {dossier1.tax_info.fiscal_status.value}")
    assert dossier1.driver_info is not None
    print(f"CNH: {dossier1.driver_info.cnh_number} | Status: {dossier1.driver_info.license_status.value} | Pontos: {dossier1.driver_info.points}")
    assert dossier1.civil_info is not None
    print(f"Estado Civil: {dossier1.civil_info.marital_status.value} | Cartório: {dossier1.civil_info.cartorio_municipio}")
    assert dossier1.access_restrictions_applied is None
    print("-> Nenhuma restrição aplicada. Acesso irrestrito concedido pelo Catálogo.")

    # -------------------------------------------------------------------------
    # Cenário 2: Polícia Rodoviária (Segurança / Trânsito)
    # -------------------------------------------------------------------------
    print_separator("Cenário 2: Polícia Rodoviária consultando Cidadão (CPF 555.666.777-88)")
    dossier2 = bus.consult_citizen_dossier("POLICIA_RODOVIARIA", "55566677788")
    assert dossier2 is not None
    print(f"Cidadã: {dossier2.tax_info.full_name} | Situação Fiscal: {dossier2.tax_info.fiscal_status.value}")
    assert dossier2.driver_info is not None
    print(f"CNH: {dossier2.driver_info.cnh_number} | Status: {dossier2.driver_info.license_status.value} (Pontos: {dossier2.driver_info.points})")
    assert dossier2.civil_info is None
    print(f"Restrições aplicadas pelo ESB: {dossier2.access_restrictions_applied}")
    assert "CARTORIO_CIVIL_OMITTED_DUE_TO_CLEARANCE" in dossier2.access_restrictions_applied

    # -------------------------------------------------------------------------
    # Cenário 3: Prefeitura Municipal (Acesso Básico Cidadão)
    # -------------------------------------------------------------------------
    print_separator("Cenário 3: Prefeitura de Campinas consultando Cidadão (CPF 111.222.333-44)")
    dossier3 = bus.consult_citizen_dossier("PREFEITURA_CAMPINAS", "11122233344")
    assert dossier3 is not None
    print(f"Cidadão: {dossier3.tax_info.full_name} | Data Nasc: {dossier3.tax_info.birth_date}")
    assert dossier3.driver_info is None
    assert dossier3.civil_info is None
    print(f"Restrições aplicadas pelo ESB: {dossier3.access_restrictions_applied}")
    assert len(dossier3.access_restrictions_applied) == 2

    # -------------------------------------------------------------------------
    # Cenário 4: Consumidor Não Cadastrado / Não Autorizado
    # -------------------------------------------------------------------------
    print_separator("Cenário 4: Entidade Privada não autorizada tenta acessar barramento governamental")
    try:
        bus.consult_citizen_dossier("EMPRESA_PRIVADA_X", "11122233344")
        assert False, "Deveria ter lançado PermissionError"
    except PermissionError as exc:
        print(f"Bloqueio com sucesso pelo ESB: {exc}")

    # -------------------------------------------------------------------------
    # Cenário 5: Trilha de Auditoria e Conformidade LGPD
    # -------------------------------------------------------------------------
    print_separator("Cenário 5: Verificação dos Logs de Auditoria do Barramento")
    entries = audit_logger.entries
    print(f"Total de requisições registradas na auditoria: {len(entries)}")
    for entry in entries:
        status_str = "CONCEDIDO" if entry.access_granted else "NEGADO"
        print(f"  [{entry.timestamp[:19]}] Consumidor: {entry.consumer_id:<20} | Status: {status_str:<9} | CPF: {entry.cpf_consultado}")
    assert len(entries) == 4

    print_separator("Todos os cenários de Interoperabilidade Governamental validados com sucesso!")


if __name__ == "__main__":
    main()
