"""Simulador de Banco de Dados Relacional com Transações ACID."""

import contextlib
import copy
from typing import Dict, Generator, List, Optional, Any


class TransactionalDatabase:
    """Banco relacional em memória com suporte a transações ACID (Commit e Rollback)."""

    def __init__(self) -> None:
        # Tabelas comprometidas (Committed state)
        self.wallets: Dict[str, float] = {
            "WALLET-ALICE": 1000.0,
            "WALLET-BOB": 250.0,
        }
        self.outbox_table: Dict[str, Any] = {}

    @contextlib.contextmanager
    def transaction(self) -> Generator["TransactionalDatabaseSession", None, None]:
        session = TransactionalDatabaseSession(self)
        try:
            yield session
            session.commit()
        except Exception as exc:
            session.rollback()
            raise exc


class TransactionalDatabaseSession:
    """Sessão transacional com buffer de staging."""

    def __init__(self, db: TransactionalDatabase) -> None:
        self._db = db
        # Cópias em staging para isolamento transacional
        self._wallets_staging: Dict[str, float] = copy.deepcopy(db.wallets)
        self._outbox_staging: Dict[str, Any] = copy.deepcopy(db.outbox_table)

    def get_wallet_balance(self, wallet_id: str) -> float:
        return self._wallets_staging.get(wallet_id, 0.0)

    def update_wallet_balance(self, wallet_id: str, new_balance: float) -> None:
        self._wallets_staging[wallet_id] = new_balance

    def insert_outbox_record(self, record: Any) -> None:
        self._outbox_staging[record.event_id] = record

    def commit(self) -> None:
        # Aplicação atômica do staging para o banco definitivo
        self._db.wallets = self._wallets_staging
        self._db.outbox_table = self._outbox_staging

    def rollback(self) -> None:
        # Descarta o staging
        self._wallets_staging.clear()
        self._outbox_staging.clear()
