"""Wallet Service aplicando o Transactional Outbox Pattern."""

import uuid
from typing import Dict, Any
from storage.database import TransactionalDatabase
from outbox.outbox_models import OutboxRecord, OutboxStatus


class InsufficientFundsException(ValueError):
    pass


class WalletService:
    """Serviço financeiro de carteira digital.
    
    Princípio Chave: NUNCA tenta publicar no Message Broker diretamente dentro do fluxo do cliente.
    Em vez disso, persiste a alteração de saldo e o registro Outbox dentro da mesma transação ACID.
    """

    def __init__(self, db: TransactionalDatabase) -> None:
        self._db = db

    def transfer_funds(
        self, source_wallet: str, target_wallet: str, amount: float
    ) -> OutboxRecord:
        event_id = f"EVT-TX-{uuid.uuid4().hex[:8].upper()}"

        # Início da Transação Local ACID
        with self._db.transaction() as session:
            source_balance = session.get_wallet_balance(source_wallet)
            if source_balance < amount:
                raise InsufficientFundsException(
                    f"Saldo insuficiente na carteira {source_wallet} (Saldo: R$ {source_balance:.2f}, Solicitado: R$ {amount:.2f})"
                )

            target_balance = session.get_wallet_balance(target_wallet)

            # 1. Atualização do Ledger Financeiro no Banco
            session.update_wallet_balance(source_wallet, source_balance - amount)
            session.update_wallet_balance(target_wallet, target_balance + amount)

            # 2. Inserção do Evento na Tabela Outbox (Atomicamente na mesma transação)
            outbox_record = OutboxRecord(
                event_id=event_id,
                aggregate_type="WALLET",
                aggregate_id=source_wallet,
                event_type="FundsTransferred",
                payload={
                    "event_id": event_id,
                    "from_wallet": source_wallet,
                    "to_wallet": target_wallet,
                    "amount": amount,
                },
                status=OutboxStatus.PENDING,
            )
            session.insert_outbox_record(outbox_record)

        # Fim da Transação ACID: Saldo e Outbox gravados atomicamente!
        return outbox_record
