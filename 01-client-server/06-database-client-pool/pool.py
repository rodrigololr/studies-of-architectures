"""
pool.py - Gerenciador de Connection Pool do lado do cliente.

Mantém uma fila thread-safe de conexões abertas, emprestando-as
para threads sob demanda e reaproveitando-as sem overhead de novo handshake TCP.
"""

from __future__ import annotations
import queue
import threading
from typing import Optional
from client import DbConnection


class DatabaseConnectionPool:
    def __init__(self, host: str, port: int, pool_size: int = 3) -> None:
        self.host = host
        self.port = port
        self.pool_size = pool_size
        self._pool: queue.Queue[DbConnection] = queue.Queue(maxsize=pool_size)
        self._lock = threading.Lock()
        self._created_count = 0
        self._is_closed = False

        # Pré-aquece as conexões do pool
        for _ in range(pool_size):
            conn = self._create_new_connection()
            self._pool.put(conn)

    def _create_new_connection(self) -> DbConnection:
        with self._lock:
            self._created_count += 1
            cid = self._created_count
        conn = DbConnection(self.host, self.port, connection_id=cid)
        conn.open()
        return conn

    def acquire(self, timeout_sec: float = 3.0) -> DbConnection:
        """Aluga uma conexão disponível do pool ou aguarda até uma ser liberada."""
        if self._is_closed:
            raise RuntimeError("Pool de conexões está encerrado.")

        try:
            conn = self._pool.get(timeout=timeout_sec)
        except queue.Empty:
            raise TimeoutError("Nenhuma conexão de banco disponível no pool dentro do timeout.")

        # Validação com Heartbeat / Ping antes de entregar
        if not conn.ping():
            conn.close()
            conn = self._create_new_connection()

        return conn

    def release(self, conn: DbConnection) -> None:
        """Devolve a conexão de volta ao pool para reutilização por outras threads."""
        if self._is_closed:
            conn.close()
            return

        try:
            self._pool.put_nowait(conn)
        except queue.Full:
            conn.close()

    def close_all(self) -> None:
        """Fecha todas as conexões mantidas no pool."""
        self._is_closed = True
        while not self._pool.empty():
            try:
                conn = self._pool.get_nowait()
                conn.close()
            except queue.Empty:
                break
