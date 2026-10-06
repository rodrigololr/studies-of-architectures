"""Outbox Relay / Polling Publisher Engine (Processo em background confiável)."""

import time
from typing import List
from storage.database import TransactionalDatabase
from broker.message_broker import ExternalMessageBroker
from outbox.outbox_models import OutboxStatus, OutboxRecord


class OutboxRelayWorker:
    """Motor de repasse do Outbox (simulando Debezium CDC ou Polling Publisher)."""

    def __init__(
        self, db: TransactionalDatabase, broker: ExternalMessageBroker
    ) -> None:
        self._db = db
        self._broker = broker

    def process_pending_events(self) -> int:
        """Lê os eventos PENDING ou FAILED da tabela Outbox e publica no broker externo."""
        pending_records: List[OutboxRecord] = [
            rec
            for rec in self._db.outbox_table.values()
            if rec.status in (OutboxStatus.PENDING, OutboxStatus.FAILED)
        ]

        success_count = 0
        for record in pending_records:
            try:
                # Tenta publicar no broker
                self._broker.publish("wallet.transfers.v1", record.payload)
                record.status = OutboxStatus.PUBLISHED
                record.published_at = time.time()
                success_count += 1
            except Exception as exc:
                record.status = OutboxStatus.FAILED
                record.retry_count += 1
                # Evento permanece seguro na tabela Outbox para próxima tentativa

        return success_count
