"""
main.py - Camada 4: Frameworks & Drivers (Composition Root).
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from entities.models import Account, PixKeyRecord
from interface_adapters.gateways import (
    InMemoryAccountRepository,
    InMemoryPixDirectoryGateway,
    InMemoryTransferRepository,
)
from interface_adapters.presenters import TransferRestPresenter
from interface_adapters.controllers import TransferWebController
from use_cases.interactors import TransferFundsInteractor


def main() -> None:
    print("=" * 80)
    print(" CLEAN ARCHITECTURE - EXEMPLO 03: DIGITAL BANKING TRANSFERS (PIX & TED)")
    print("=" * 80)

    # 1. Configuração de Contas e Diretório PIX (Infraestrutura)
    account_repo = InMemoryAccountRepository({
        "1001-5": Account(
            account_number="1001-5",
            owner_name="João Silva",
            balance=3500.0,
            daytime_limit=5000.0,
            nighttime_limit=1000.0,
        ),
        "2002-8": Account(
            account_number="2002-8",
            owner_name="Maria Oliveira",
            balance=1200.0,
            daytime_limit=5000.0,
            nighttime_limit=1000.0,
        ),
        "9999-0": Account(
            account_number="9999-0",
            owner_name="Conta Sob Investigação",
            balance=50000.0,
            is_blocked=True,
        ),
    })

    pix_directory = InMemoryPixDirectoryGateway({
        "maria@email.com": PixKeyRecord(key_value="maria@email.com", key_type="EMAIL", account_number="2002-8"),
        "11988887777": PixKeyRecord(key_value="11988887777", key_type="PHONE", account_number="1001-5"),
    })

    transfer_repo = InMemoryTransferRepository()
    presenter = TransferRestPresenter()

    # 2. Montagem dos Casos de Uso e Controladores
    use_case = TransferFundsInteractor(
        account_repo=account_repo,
        pix_gateway=pix_directory,
        transfer_repo=transfer_repo,
        presenter=presenter,
    )
    controller = TransferWebController(transfer_use_case=use_case)

    print("\n--- CENÁRIO 1: Transferência PIX Diurna via Chave de E-mail (Sucesso) ---")
    controller.handle_post_transfer({
        "from_account": "1001-5",
        "destination": "maria@email.com",
        "amount": 800.0,
        "method": "PIX",
        "is_night_time": False,
    })
    print(f"HTTP Status: {presenter.status_code}")
    print(json.dumps(presenter.response_body, indent=2, ensure_ascii=False))

    print("\n--- CENÁRIO 2: Transferência TED por Número de Conta Favorecida (Sucesso) ---")
    controller.handle_post_transfer({
        "from_account": "2002-8",
        "destination": "1001-5",
        "amount": 350.0,
        "method": "TED",
        "is_night_time": False,
    })
    print(f"HTTP Status: {presenter.status_code}")
    print(json.dumps(presenter.response_body, indent=2, ensure_ascii=False))

    print("\n--- CENÁRIO 3: Rejeição por Saldo Insuficiente (Regra de Entidade) ---")
    controller.handle_post_transfer({
        "from_account": "1001-5",
        "destination": "maria@email.com",
        "amount": 9000.0,
        "method": "PIX",
        "is_night_time": False,
    })
    print(f"HTTP Status: {presenter.status_code}")
    print(json.dumps(presenter.response_body, indent=2, ensure_ascii=False))

    print("\n--- CENÁRIO 4: Violação de Limite Noturno do BACEN (Teto de R$ 1.000 entre 20h e 06h) ---")
    controller.handle_post_transfer({
        "from_account": "1001-5",
        "destination": "maria@email.com",
        "amount": 1500.0,
        "method": "PIX",
        "is_night_time": True,  # Período noturno
    })
    print(f"HTTP Status: {presenter.status_code}")
    print(json.dumps(presenter.response_body, indent=2, ensure_ascii=False))

    print("\n--- CENÁRIO 5: Rejeição por Conta Bloqueada Administrativamente ---")
    controller.handle_post_transfer({
        "from_account": "9999-0",
        "destination": "1001-5",
        "amount": 500.0,
        "method": "TED",
        "is_night_time": False,
    })
    print(f"HTTP Status: {presenter.status_code}")
    print(json.dumps(presenter.response_body, indent=2, ensure_ascii=False))

    print("\n--- CENÁRIO 6: Chave PIX Inexistente no Diretório Central (DICT) ---")
    controller.handle_post_transfer({
        "from_account": "1001-5",
        "destination": "chave.fantasma@desconhecido.com",
        "amount": 100.0,
        "method": "PIX",
    })
    print(f"HTTP Status: {presenter.status_code}")
    print(json.dumps(presenter.response_body, indent=2, ensure_ascii=False))

    print("\n--- CENÁRIO 7: Histórico Auditável de Movimentações da Conta 1001-5 ---")
    history = transfer_repo.list_by_account("1001-5")
    print(f"Total de registros auditados: {len(history)}")
    for t in history:
        print(f" -> [{t.transacted_at.strftime('%H:%M:%S')}] {t.method.value:3} | De: {t.from_account_number} Para: {t.to_account_number} | R$ {t.amount:7.2f} | Status: {t.status.value:9} {f'({t.error_reason})' if t.error_reason else ''}")

    print("\n" + "=" * 80)
    print(" Exemplo 03 finalizado com sucesso!")
    print("=" * 80)


if __name__ == "__main__":
    main()
