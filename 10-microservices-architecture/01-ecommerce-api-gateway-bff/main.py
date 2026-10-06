"""Demonstração de Microsserviços: API Gateway e Backend-for-Frontend (BFF).

Cenários demonstrados:
1. Requisição Mobile (BFF compacto otimizado para banda móvel e baixa latência)
2. Requisição Web Desktop (BFF rico com galeria, especificações detalhadas e comentários)
3. Comparação de overhead e tamanho de payload (Mobile vs. Web)
4. Bloqueio de segurança e autenticação diretamente no Gateway (401 Unauthorized)
5. Roteamento de recurso não encontrado no catálogo (404 Not Found)
"""

import sys
import json
from pathlib import Path

# Garante resolução de imports absolutos
sys.path.insert(0, str(Path(__file__).parent))

from services.catalog_service import CatalogService
from services.pricing_service import PricingService
from services.inventory_service import InventoryService
from services.review_service import ReviewService
from gateway.mobile_bff import MobileBff
from gateway.web_desktop_bff import WebDesktopBff
from gateway.api_gateway import ApiGateway


def print_separator(title: str) -> None:
    print(f"\n{'='*75}\n>>> {title}\n{'='*75}")


def main() -> None:
    print("Inicializando Ecossistema de Microsserviços, BFFs e API Gateway...")

    # Inicialização dos Microsserviços Independentes (Database-per-Service)
    catalog = CatalogService()
    pricing = PricingService()
    inventory = InventoryService()
    review = ReviewService()

    # Inicialização dos BFFs especializados
    mobile_bff = MobileBff(catalog, pricing, inventory, review)
    web_bff = WebDesktopBff(catalog, pricing, inventory, review)

    # Inicialização do API Gateway de Borda
    gateway = ApiGateway(mobile_bff, web_bff)

    # -------------------------------------------------------------------------
    # Cenário 1: Cliente Mobile consulta PDP do Galaxy S24 Ultra
    # -------------------------------------------------------------------------
    print_separator("Cenário 1: Cliente Mobile App acessando /api/v1/mobile/products/PROD-001")
    mobile_headers = {"Authorization": "Bearer token-mobile-secret-xyz"}
    res_mobile = gateway.handle_request("GET", "/api/v1/mobile/products/PROD-001", mobile_headers)
    print(f"Status Code: {res_mobile.status_code}")
    print(f"Tamanho do Payload: {res_mobile.payload_size_bytes} bytes")
    print("Corpo da Resposta JSON (Compacto para Mobile):")
    print(json.dumps(res_mobile.body, indent=2, ensure_ascii=False))
    assert res_mobile.status_code == 200
    assert "technical_specifications" not in res_mobile.body
    assert res_mobile.body["id"] == "PROD-001"

    # -------------------------------------------------------------------------
    # Cenário 2: Cliente Web Desktop acessando PDP do mesmo produto
    # -------------------------------------------------------------------------
    print_separator("Cenário 2: Cliente Web Desktop acessando /api/v1/web/products/PROD-001")
    web_headers = {"Authorization": "Bearer token-web-secret-abc"}
    res_web = gateway.handle_request("GET", "/api/v1/web/products/PROD-001", web_headers)
    print(f"Status Code: {res_web.status_code}")
    print(f"Tamanho do Payload: {res_web.payload_size_bytes} bytes")
    print("Corpo da Resposta JSON (Rico e Estruturado para Web):")
    print(json.dumps(res_web.body, indent=2, ensure_ascii=False))
    assert res_web.status_code == 200
    assert "technical_specifications" in res_web.body["content"]
    assert len(res_web.body["media_gallery"]) == 3
    assert len(res_web.body["customer_feedback"]["reviews_list"]) == 3

    # -------------------------------------------------------------------------
    # Cenário 3: Análise Comparativa de Eficiência de Banda
    # -------------------------------------------------------------------------
    print_separator("Cenário 3: Comparação de Eficiência de Banda (Mobile vs. Web)")
    ratio = res_web.payload_size_bytes / res_mobile.payload_size_bytes
    economia_pct = ((res_web.payload_size_bytes - res_mobile.payload_size_bytes) / res_web.payload_size_bytes) * 100
    print(f"Payload Web:    {res_web.payload_size_bytes} bytes")
    print(f"Payload Mobile: {res_mobile.payload_size_bytes} bytes")
    print(f"O BFF Web entregou {ratio:.1f}x mais dados que o BFF Mobile.")
    print(f"-> Economia de dados no Mobile proporcionada pelo BFF: {economia_pct:.1f}%")
    assert res_mobile.payload_size_bytes < res_web.payload_size_bytes

    # -------------------------------------------------------------------------
    # Cenário 4: Segurança - Tentativa sem Token de Autenticação no Gateway
    # -------------------------------------------------------------------------
    print_separator("Cenário 4: Tentativa de Acesso sem Autenticação (401)")
    unauth_res = gateway.handle_request("GET", "/api/v1/mobile/products/PROD-001", {})
    print(f"Status Code: {unauth_res.status_code}")
    print(f"Resposta de Erro: {unauth_res.body}")
    assert unauth_res.status_code == 401

    # -------------------------------------------------------------------------
    # Cenário 5: Produto Não Encontrado no Catálogo (404)
    # -------------------------------------------------------------------------
    print_separator("Cenário 5: Produto Inexistente (404 Not Found)")
    not_found_res = gateway.handle_request(
        "GET", "/api/v1/mobile/products/PROD-999", mobile_headers
    )
    print(f"Status Code: {not_found_res.status_code}")
    print(f"Resposta: {not_found_res.body}")
    assert not_found_res.status_code == 404

    print_separator("Todos os cenários de API Gateway & BFF foram validados com sucesso!")


if __name__ == "__main__":
    main()
