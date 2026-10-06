"""Demonstração de SOA: Agregador de Cotação de Seguros Multi-Provedores (Scatter-Gather via ESB).

Cenários demonstrados:
1. Perfil padrão (todas as 3 seguradoras aprovam e concorrem com menor preço)
2. Motorista jovem < 21 anos (Porto recusa por política de risco, Allianz e Bradesco cotam)
3. Veículo de luxo > 300k (Bradesco recusa por teto automático, Porto e Allianz cotam)
4. Veículo antigo > 15 anos (Allianz recusa por idade máxima, Porto e Bradesco cotam)
"""

import sys
from pathlib import Path

# Garante resolução de imports absolutos
sys.path.insert(0, str(Path(__file__).parent))

from canonical.underwriting_models import (
    VehicleInfo,
    DriverProfile,
    CoverageType,
    CanonicalQuoteRequest,
)
from providers.porto_seguro_provider import PortoSeguroSoapService
from providers.allianz_provider import AllianzRestService
from providers.bradesco_provider import BradescoRpcService
from esb.adapters.porto_adapter import PortoSeguroAdapter
from esb.adapters.allianz_adapter import AllianzAdapter
from esb.adapters.bradesco_adapter import BradescoAdapter
from esb.insurance_broker_esb import InsuranceBrokerESB


def print_separator(title: str) -> None:
    print(f"\n{'='*75}\n>>> {title}\n{'='*75}")


def main() -> None:
    print("Inicializando Barramento SOA de Subscrição Multi-Seguradoras...")

    # Inicialização dos Provedores Heterogêneos
    porto_svc = PortoSeguroSoapService()
    allianz_svc = AllianzRestService()
    bradesco_svc = BradescoRpcService()

    # Inicialização dos Adaptadores do ESB
    porto_adp = PortoSeguroAdapter(porto_svc)
    allianz_adp = AllianzAdapter(allianz_svc)
    bradesco_adp = BradescoAdapter(bradesco_svc)

    # Barramento Corporativo
    esb = InsuranceBrokerESB(porto_adp, allianz_adp, bradesco_adp)

    # -------------------------------------------------------------------------
    # Cenário 1: Perfil Padrão - Corolla 2022 (Todas as seguradoras aprovam)
    # -------------------------------------------------------------------------
    print_separator("Cenário 1: Cotação para Veículo Padrão (Toyota Corolla 2022 - R$ 120.000)")
    req1 = CanonicalQuoteRequest(
        request_id="REQ-COROLLA-01",
        vehicle=VehicleInfo(make="Toyota", model="Corolla XEi", year=2022, fipe_value_brl=120000.0),
        driver=DriverProfile(age=35, gender="M", license_years=15, has_garage=True),
        coverage=CoverageType.STANDARD,
    )
    res1 = esb.quote_across_carriers(req1)
    print(f"Total consultado: {res1.total_requested} | Propostas recebidas: {len(res1.successful_proposals)}")
    for p in res1.successful_proposals:
        print(f"  - [{p.carrier_name}] Prêmio: R$ {p.annual_premium_brl:,.2f} | Franquia: R$ {p.deductible_brl:,.2f} | Ref: {p.carrier_protocol}")
    print(f"-> Melhor Oferta: {res1.best_value_carrier} por R$ {res1.cheapest_premium_brl:,.2f}/ano")
    assert len(res1.successful_proposals) == 3
    assert len(res1.failed_carriers) == 0
    assert res1.best_value_carrier is not None

    # -------------------------------------------------------------------------
    # Cenário 2: Motorista Jovem < 21 Anos (Porto Seguradora recusa risco)
    # -------------------------------------------------------------------------
    print_separator("Cenário 2: Motorista Jovem de 19 anos (Honda Civic 2020 - R$ 95.000)")
    req2 = CanonicalQuoteRequest(
        request_id="REQ-CIVIC-02",
        vehicle=VehicleInfo(make="Honda", model="Civic EXL", year=2020, fipe_value_brl=95000.0),
        driver=DriverProfile(age=19, gender="M", license_years=1, has_garage=False),
        coverage=CoverageType.STANDARD,
    )
    res2 = esb.quote_across_carriers(req2)
    print(f"Propostas aprovadas: {len(res2.successful_proposals)} | Recusas parciais: {len(res2.failed_carriers)}")
    for p in res2.successful_proposals:
        print(f"  - [{p.carrier_name}] Prêmio: R$ {p.annual_premium_brl:,.2f}")
    for fail in res2.failed_carriers:
        print(f"  * Recusa capturada pelo ESB: {fail}")
    assert len(res2.successful_proposals) == 2
    assert any("Porto Seguro" in f for f in res2.failed_carriers)

    # -------------------------------------------------------------------------
    # Cenário 3: Veículo de Alto Valor > R$ 300.000 (Bradesco recusa teto automático)
    # -------------------------------------------------------------------------
    print_separator("Cenário 3: Veículo Premium > 300k (Porsche Macan 2023 - R$ 450.000)")
    req3 = CanonicalQuoteRequest(
        request_id="REQ-MACAN-03",
        vehicle=VehicleInfo(make="Porsche", model="Macan GTS", year=2023, fipe_value_brl=450000.0),
        driver=DriverProfile(age=45, gender="F", license_years=25, has_garage=True),
        coverage=CoverageType.COMPREHENSIVE,
    )
    res3 = esb.quote_across_carriers(req3)
    print(f"Propostas aprovadas: {len(res3.successful_proposals)} | Recusas: {len(res3.failed_carriers)}")
    for p in res3.successful_proposals:
        print(f"  - [{p.carrier_name}] Prêmio: R$ {p.annual_premium_brl:,.2f}")
    for fail in res3.failed_carriers:
        print(f"  * Recusa capturada pelo ESB: {fail}")
    assert len(res3.successful_proposals) == 2
    assert any("Bradesco Seguros" in f for f in res3.failed_carriers)

    # -------------------------------------------------------------------------
    # Cenário 4: Veículo Antigo > 15 anos (Allianz recusa por ano limite)
    # -------------------------------------------------------------------------
    print_separator("Cenário 4: Veículo com 18 anos de uso (VW Gol 2008 - R$ 22.000)")
    req4 = CanonicalQuoteRequest(
        request_id="REQ-GOL-04",
        vehicle=VehicleInfo(make="Volkswagen", model="Gol 1.0", year=2008, fipe_value_brl=22000.0),
        driver=DriverProfile(age=38, gender="M", license_years=18, has_garage=True),
        coverage=CoverageType.BASIC,
    )
    res4 = esb.quote_across_carriers(req4)
    print(f"Propostas aprovadas: {len(res4.successful_proposals)} | Recusas: {len(res4.failed_carriers)}")
    for p in res4.successful_proposals:
        print(f"  - [{p.carrier_name}] Prêmio: R$ {p.annual_premium_brl:,.2f}")
    for fail in res4.failed_carriers:
        print(f"  * Recusa capturada pelo ESB: {fail}")
    assert len(res4.successful_proposals) == 2
    assert any("Allianz" in f for f in res4.failed_carriers)

    print_separator("Todos os cenários do Barramento de Seguros foram validados com sucesso!")


if __name__ == "__main__":
    main()
