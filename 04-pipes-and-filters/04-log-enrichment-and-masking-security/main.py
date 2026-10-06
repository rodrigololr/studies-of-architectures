"""
main.py - Demonstração executável do Pipeline de Segurança de Logs (Pipes and Filters).

Processa logs em formato JSON, aplica anonimização de dados LGPD (CPF, cartões, emails),
enriquece com país/cidade e aciona detecção de ataques cibernéticos em tempo real.
"""

import json
from pipeline.base import LogPipeline
from pipeline.context import LogEvent, GeoLocation
from filters.json_parser_filter import JsonLogParserFilter
from filters.pii_masker_filter import PiiMaskerFilter
from filters.geo_ip_filter import GeoIpFilter
from filters.threat_detector_filter import ThreatDetectorFilter


def main() -> None:
    print("=" * 84)
    print("DEMONSTRAÇÃO: Pipes and Filters (Sanitização LGPD e Detecção de Ameaças em Logs)")
    print("=" * 84)

    # 1. Base simulada de GeoIP
    ip_db = {
        "189.40.12.5": GeoLocation(country="Brasil", city="Rio de Janeiro"),
        "203.0.113.195": GeoLocation(country="Rússia", city="Moscou"),
        "198.51.100.42": GeoLocation(country="Estados Unidos", city="Nova York"),
    }

    # 2. Montagem do Pipeline
    pipeline = LogPipeline()
    pipeline.add_filter(JsonLogParserFilter())
    pipeline.add_filter(PiiMaskerFilter())
    pipeline.add_filter(GeoIpFilter(ip_db))
    pipeline.add_filter(ThreatDetectorFilter())

    # 3. Lote de logs brutos simulando fluxo de microsserviços
    raw_logs = [
        # Log 1: Checkout legítimo com CPF e e-mail
        json.dumps({
            "timestamp": "2026-10-06T10:00:01",
            "level": "INFO",
            "service": "checkout-service",
            "client_ip": "189.40.12.5",
            "message": "Pedido criado para o cliente com CPF 123.456.789-00 e e-mail roberto.silva@empresa.com",
        }),
        # Log 2: Pagamento com número de cartão de crédito no corpo do log
        json.dumps({
            "timestamp": "2026-10-06T10:00:02",
            "level": "INFO",
            "service": "payment-gateway",
            "client_ip": "198.51.100.42",
            "message": "Tentativa de débito com o cartão 4532 9876 5432 1098 autorizada com sucesso.",
        }),
        # Log 3: Ataque de injeção SQL suspeito vindo de IP externo
        json.dumps({
            "timestamp": "2026-10-06T10:00:03",
            "level": "WARN",
            "service": "auth-service",
            "client_ip": "203.0.113.195",
            "message": "Falha de autenticação ao tentar username 'admin' OR 1=1 --",
        }),
        # Log 4: Linha malformada / não JSON
        "ERROR 2026-10-06 Corrupted non-json log line directly from stderr",
    ]

    print("\n--- Processando Lote de Logs no Pipeline de Observabilidade ---")

    for raw in raw_logs:
        result: LogEvent = pipeline.execute(raw)

        if not result.is_valid:
            print(f"\n❌ [LOG REJEITADO PELO PARSER]: {result.error_message}")
            continue

        print(f"\n[EVENTO INDEXADO] [{result.level}] Serviço: {result.service_name} | Origem: {result.geo.city}, {result.geo.country}")
        print(f"  📝 Mensagem Sanitizada: \"{result.message}\"")

        if result.threat_detected:
            print(f"  🚨 ALERTA SIEM: Ameaça Detectada! Tipo: {result.threat_type}")

    print("\n" + "=" * 84)


if __name__ == "__main__":
    main()
