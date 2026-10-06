"""
main.py - Demonstração executável do Pipeline ETL Bancário (Pipes and Filters).

Monta a cadeia de filtros sequenciais, processa um lote de linhas brutas de CSV,
converte moeda internacional, higieniza descrições e separa registros válidos de quarentena.
"""

from pipeline.base import Pipeline
from pipeline.context import TransactionRecord
from filters.csv_parser_filter import CsvRowParserFilter
from filters.sanitizer_filter import SanitizerFilter
from filters.date_validator_filter import DateValidatorFilter
from filters.currency_converter_filter import CurrencyConverterFilter
from filters.categorizer_filter import CategorizerFilter


def main() -> None:
    print("=" * 80)
    print("DEMONSTRAÇÃO: Arquitetura Pipes and Filters (ETL de Extrato Bancário)")
    print("=" * 80)

    # 1. Configuração das taxas de câmbio
    exchange_rates = {
        "BRL": 1.0,
        "USD": 5.40,  # 1 Dólar = R$ 5,40
        "EUR": 5.85,  # 1 Euro = R$ 5,85
    }

    # 2. Montagem do Pipeline encadeando os 5 filtros
    pipeline = Pipeline()
    pipeline.add_filter(CsvRowParserFilter())
    pipeline.add_filter(SanitizerFilter())
    pipeline.add_filter(DateValidatorFilter())
    pipeline.add_filter(CurrencyConverterFilter(exchange_rates))
    pipeline.add_filter(CategorizerFilter())

    # 3. Lote bruto de dados de extrato (Data Source)
    raw_csv_batch = [
        "2026-10-01;  pagto   salario  empresa xyz ; 6500.00 ; BRL",
        "2026-10-02; ASSINATURA AWS CLOUD ; 150.00 ; USD",  # Internacional: deve converter para R$ 810.00
        "2026-10-03;CONDOMINIO RESIDENCIAL; 850.50 ; BRL",
        "DATA_CORROMPIDA; UBER VIAGENS ; 45.90 ; BRL",     # Data inválida: deve cair em quarentena
        "2026-10-05;RESTAURANTE COZINHA BRASIL; 120.00 ; BRL",
    ]

    print("\n--- Executando Pipeline sobre Lote de Extratos ---")
    valid_records: list[TransactionRecord] = []
    quarantine_records: list[TransactionRecord] = []

    # 4. Execução do fluxo através dos dutos (Pipes)
    for raw_line in raw_csv_batch:
        result: TransactionRecord = pipeline.execute(raw_line)
        if result:
            if result.is_valid:
                valid_records.append(result)
            else:
                quarantine_records.append(result)

    # 5. Data Sink: Apresentação dos resultados processados
    print("\n✅ REGISTROS CONTÁBEIS PROCESSADOS COM SUCESSO (SINK)")
    print("-" * 80)
    print(f"{'DATA':<12} | {'DESCRIÇÃO':<28} | {'ORIGINAL':<12} | {'VALOR (BRL)':<14} | CATEGORIA")
    print("-" * 80)
    for r in valid_records:
        orig_str = f"{r.currency} {r.original_amount:,.2f}"
        brl_str = f"R$ {r.amount_brl:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        print(f"{r.date_str:<12} | {r.description:<28} | {orig_str:<12} | {brl_str:<14} | {r.category}")

    print("-" * 80)
    total_brl = sum(r.amount_brl for r in valid_records)
    print(f"Total Financeiro Consolidado em BRL: R$ {total_brl:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    # 6. Registros em Quarentena / Erros
    if quarantine_records:
        print("\n⚠️ REGISTROS ENVIADOS PARA QUARENTENA (DEAD LETTER SINK)")
        print("-" * 80)
        for q in quarantine_records:
            print(f"  • Linha Bruta: '{q.raw_line}'")
            print(f"    Motivo da Rejeição: {q.error_message}")
    print("=" * 80)


if __name__ == "__main__":
    main()
