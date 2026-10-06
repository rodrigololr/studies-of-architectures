"""Demonstração de EDA: Transactional Outbox Pattern e Eliminação da Escrita Dupla (Dual-Write).

Cenários demonstrados:
1. Operação Normal (Broker Online): Transação bancária ACID grava saldo e outbox; Relay repassa com sucesso
2. Rollback Transacional: Falha de regra de negócio desfaz saldo e NENHUM evento fantasma é criado
3. Resiliência a Quedas do Broker: Broker cai; a transferência no banco tem sucesso e o evento fica retido com segurança no Outbox
4. Recuperação e Autocura: Broker volta ao ar; Relay processa os eventos pendentes e garante consistência eventual perfeita
"""

import sys
from pathlib import Path

# Garante resolução de imports absolutos
sys.path.insert(0, str(Path(__file__).parent))

from storage.database import TransactionalDatabase
from broker.message_broker import ExternalMessageBroker
from outbox.outbox_relay import OutboxRelayWorker
from outbox.outbox_models import OutboxStatus
from wallet.wallet_service import WalletService, InsufficientFundsException


def print_separator(title: str) -> None:
    print(f"\n{'='*75}\n>>> {title}\n{'='*75}")


def main() -> None:
    print("Inicializando Sistema Financeiro com Transactional Outbox Pattern...")

    # 1. Banco relacional ACID
    db = TransactionalDatabase()

    # 2. Message Broker Externo
    broker = ExternalMessageBroker()

    # 3. Componentes de Negócio e Relay
    wallet_svc = WalletService(db)
    relay_worker = OutboxRelayWorker(db, broker)

    # -------------------------------------------------------------------------
    # Cenário 1: Operação Normal com Broker Saudável
    # -------------------------------------------------------------------------
    print_separator("Cenário 1: Transferência Normal (Alice -> Bob: R$ 150,00)")
    rec1 = wallet_svc.transfer_funds("WALLET-ALICE", "WALLET-BOB", 150.0)
    print(f"Transferência concluída no banco!")
    print(f"  Saldo Alice: R$ {db.wallets['WALLET-ALICE']:.2f}")
    print(f"  Saldo Bob:   R$ {db.wallets['WALLET-BOB']:.2f}")
    print(f"  Registro na Tabela Outbox: ID {rec1.event_id} | Status: {rec1.status.value}")
    assert db.wallets["WALLET-ALICE"] == 850.0
    assert db.wallets["WALLET-BOB"] == 400.0
    assert rec1.status == OutboxStatus.PENDING

    # Executa o Relay Worker para enviar ao broker
    published = relay_worker.process_pending_events()
    print(f"\nRelay Worker executado! Eventos publicados no broker: {published}")
    print(f"  Status do registro Outbox após repasse: {rec1.status.value}")
    print(f"  Total no Broker: {len(broker.delivered_events)} eventos entregues.")
    assert published == 1
    assert rec1.status == OutboxStatus.PUBLISHED
    assert len(broker.delivered_events) == 1

    # -------------------------------------------------------------------------
    # Cenário 2: Rollback e Prevenção de Evento Fantasma
    # -------------------------------------------------------------------------
    print_separator("Cenário 2: Saldo Insuficiente - Rollback sem Eventos Fantasmas")
    try:
        wallet_svc.transfer_funds("WALLET-ALICE", "WALLET-BOB", 5000.0)
        assert False, "Deveria ter lançado InsufficientFundsException"
    except InsufficientFundsException as exc:
        print(f"Transação abortada pelo banco: {exc}")

    # Garante que nenhum registro foi adicionado ao Outbox
    print(f"Total de registros na tabela Outbox: {len(db.outbox_table)} (Apenas o anterior)")
    assert len(db.outbox_table) == 1

    # -------------------------------------------------------------------------
    # Cenário 3: Queda do Message Broker (Kafka Offline)
    # -------------------------------------------------------------------------
    print_separator("Cenário 3: Message Broker Cai (Queda de Rede) durante Nova Transferência")
    broker.is_alive = False
    print("ALERTA: Message Broker externo ficou OFFLINE.")

    # Alice transfere R$ 200,00 para Bob
    rec2 = wallet_svc.transfer_funds("WALLET-ALICE", "WALLET-BOB", 200.0)
    print(f"Transferência bancária local concluída com sucesso!")
    print(f"  Novo Saldo Alice: R$ {db.wallets['WALLET-ALICE']:.2f}")
    print(f"  Novo Saldo Bob:   R$ {db.wallets['WALLET-BOB']:.2f}")
    print(f"  Evento registrado no Outbox: ID {rec2.event_id} | Status: {rec2.status.value}")
    assert db.wallets["WALLET-ALICE"] == 650.0
    assert db.wallets["WALLET-BOB"] == 600.0

    # Relay tenta enviar e falha com segurança
    failed_publish = relay_worker.process_pending_events()
    print(f"Relay Worker executado sob queda do broker: {failed_publish} publicados.")
    print(f"  Status do registro Outbox: {rec2.status.value} (Tentativas: {rec2.retry_count})")
    assert failed_publish == 0
    assert rec2.status == OutboxStatus.FAILED
    assert rec2.retry_count == 1

    # -------------------------------------------------------------------------
    # Cenário 4: Recuperação do Broker e Replay Confiável
    # -------------------------------------------------------------------------
    print_separator("Cenário 4: Broker Restabelecido - Replay Automático do Outbox")
    broker.is_alive = True
    print("Message Broker voltou a operar (ONLINE).")

    recovered = relay_worker.process_pending_events()
    print(f"Relay Worker reprocessou eventos acumulados: {recovered} eventos enviados!")
    print(f"  Status final do registro Outbox: {rec2.status.value}")
    print(f"  Total de eventos recebidos no Broker: {len(broker.delivered_events)}")
    assert recovered == 1
    assert rec2.status == OutboxStatus.PUBLISHED
    assert len(broker.delivered_events) == 2

    print_separator("Todos os cenários do Transactional Outbox Pattern foram validados com sucesso!")


if __name__ == "__main__":
    main()
