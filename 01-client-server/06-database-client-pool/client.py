"""
client.py - Conexão individual do cliente com o banco de dados.

Encapsula o socket TCP persistente, envio de comandos e checagem de saúde (Ping).
"""

from __future__ import annotations
import socket
import uuid
from typing import Any, List, Optional
from protocol import DbCommand, DbResult, DbAction


class DbConnection:
    def __init__(self, host: str, port: int, connection_id: int) -> None:
        self.host = host
        self.port = port
        self.connection_id = connection_id
        self._sock: Optional[socket.socket] = None
        self._is_open = False

    def open(self) -> None:
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.settimeout(2.0)
        self._sock.connect((self.host, self.port))
        self._is_open = True

    def ping(self) -> bool:
        """Verifica se a conexão ainda está viva no servidor."""
        if not self._is_open or not self._sock:
            return False
        try:
            cmd = DbCommand(command_id="ping", action=DbAction.PING)
            self._sock.sendall(cmd.serialize())
            res = self._read_result()
            return res is not None and res.success
        except Exception:
            self._is_open = False
            return False

    def execute_query(self, query: str) -> List[Any]:
        """Envia query e retorna os dados resultantes."""
        if not self._is_open or not self._sock:
            raise RuntimeError("Conexão fechada.")

        cmd_id = str(uuid.uuid4())[:8]
        cmd = DbCommand(command_id=cmd_id, action=DbAction.EXECUTE, query_text=query)
        self._sock.sendall(cmd.serialize())

        res = self._read_result()
        if not res or not res.success:
            raise RuntimeError(res.error if res else "Erro na execução da query")

        return res.data

    def _read_result(self) -> Optional[DbResult]:
        buffer = ""
        while "\n" not in buffer:
            chunk = self._sock.recv(2048) if self._sock else b""
            if not chunk:
                return None
            buffer += chunk.decode("utf-8")

        line, _ = buffer.split("\n", 1)
        return DbResult.deserialize(line)

    def close(self) -> None:
        if self._is_open and self._sock:
            try:
                cmd = DbCommand(command_id="close", action=DbAction.CLOSE)
                self._sock.sendall(cmd.serialize())
                self._sock.close()
            except OSError:
                pass
            finally:
                self._is_open = False
