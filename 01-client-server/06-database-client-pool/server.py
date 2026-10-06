"""
server.py - Servidor simulado de Banco de Dados.

Mantém sessões ativas persistentes, responde a checagens de integridade (PING)
e executa queries simuladas com latência realista.
"""

from __future__ import annotations
import socket
import threading
import time
from typing import Optional
from protocol import DbCommand, DbResult, DbAction


class DatabaseServer:
    def __init__(self, host: str = "127.0.0.1", port: int = 0) -> None:
        self.host = host
        self.port = port
        self._server_socket: Optional[socket.socket] = None
        self._is_running = False
        self._active_connections = 0
        self._lock = threading.Lock()

    @property
    def bound_port(self) -> int:
        if self._server_socket:
            return self._server_socket.getsockname()[1]
        return self.port

    def start(self) -> None:
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.bind((self.host, self.port))
        self._server_socket.listen(20)
        self._is_running = True

        threading.Thread(target=self._accept_loop, daemon=True).start()

    def _accept_loop(self) -> None:
        while self._is_running and self._server_socket:
            try:
                sock, _ = self._server_socket.accept()
                with self._lock:
                    self._active_connections += 1
                threading.Thread(target=self._handle_client, args=(sock,), daemon=True).start()
            except OSError:
                break

    def _handle_client(self, sock: socket.socket) -> None:
        buffer = ""
        try:
            while self._is_running:
                data = sock.recv(2048)
                if not data:
                    break

                buffer += data.decode("utf-8")
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    cmd = DbCommand.deserialize(line)
                    if not cmd:
                        continue

                    if cmd.action == DbAction.PING:
                        res = DbResult(command_id=cmd.command_id, success=True, data=["PONG"])
                    elif cmd.action == DbAction.EXECUTE:
                        # Simula tempo de consulta no disco/índice (10ms)
                        time.sleep(0.01)
                        res = DbResult(
                            command_id=cmd.command_id,
                            success=True,
                            data=[{"id": 101, "status": "CONFIRMADO", "query": cmd.query_text}],
                        )
                    elif cmd.action == DbAction.CLOSE:
                        return
                    else:
                        res = DbResult(
                            command_id=cmd.command_id, success=False, data=[], error="Comando não suportado"
                        )

                    sock.sendall(res.serialize())
        except Exception:
            pass
        finally:
            with self._lock:
                self._active_connections -= 1
            try:
                sock.close()
            except OSError:
                pass

    def stop(self) -> None:
        self._is_running = False
        if self._server_socket:
            try:
                self._server_socket.close()
            except OSError:
                pass
