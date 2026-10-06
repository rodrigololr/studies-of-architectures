"""
server.py - Servidor RPC com Despachante Dinâmico e Autenticação.

Registra procedimentos invocáveis via decorador, valida credenciais
e executa funções encapsulando qualquer exceção interna em respostas estruturadas.
"""

from __future__ import annotations
import socket
import threading
import time
from typing import Any, Callable, Dict, Optional
from protocol import RpcRequest, RpcResponse


class RpcServer:
    def __init__(self, valid_token: str, host: str = "127.0.0.1", port: int = 0) -> None:
        self.valid_token = valid_token
        self.host = host
        self.port = port
        self._server_socket: Optional[socket.socket] = None
        self._is_running = False
        self._methods: Dict[str, Callable[..., Any]] = {}

    @property
    def bound_port(self) -> int:
        if self._server_socket:
            return self._server_socket.getsockname()[1]
        return self.port

    def register_method(self, name: str, func: Callable[..., Any]) -> None:
        """Registra uma função Python como procedimento remoto invocável."""
        self._methods[name] = func

    def start(self) -> None:
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.bind((self.host, self.port))
        self._server_socket.listen(5)
        self._is_running = True

        threading.Thread(target=self._accept_loop, daemon=True).start()

    def _accept_loop(self) -> None:
        while self._is_running and self._server_socket:
            try:
                client_sock, _ = self._server_socket.accept()
                threading.Thread(
                    target=self._handle_client, args=(client_sock,), daemon=True
                ).start()
            except OSError:
                break

    def _handle_client(self, client_sock: socket.socket) -> None:
        buffer = ""
        try:
            while self._is_running:
                data = client_sock.recv(4096)
                if not data:
                    break

                buffer += data.decode("utf-8")
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    request = RpcRequest.deserialize(line)
                    if not request:
                        continue

                    response = self._execute_request(request)
                    client_sock.sendall(response.serialize())
        except Exception:
            pass
        finally:
            try:
                client_sock.close()
            except OSError:
                pass

    def _execute_request(self, request: RpcRequest) -> RpcResponse:
        start_time = time.perf_counter()

        # 1. Validação de Autenticação
        if request.auth_token != self.valid_token:
            return RpcResponse(
                request_id=request.request_id,
                success=False,
                result=None,
                error="Unauthorized: Token de acesso inválido",
            )

        # 2. Verificação de Existência do Método
        if request.method not in self._methods:
            return RpcResponse(
                request_id=request.request_id,
                success=False,
                result=None,
                error=f"MethodNotFound: Procedimento '{request.method}' não registrado",
            )

        # 3. Execução Segura da Função
        try:
            func = self._methods[request.method]
            result = func(**request.params)
            duration = (time.perf_counter() - start_time) * 1000
            return RpcResponse(
                request_id=request.request_id,
                success=True,
                result=result,
                error=None,
                execution_time_ms=round(duration, 2),
            )
        except Exception as ex:
            duration = (time.perf_counter() - start_time) * 1000
            return RpcResponse(
                request_id=request.request_id,
                success=False,
                result=None,
                error=f"ExecutionError: {type(ex).__name__} - {str(ex)}",
                execution_time_ms=round(duration, 2),
            )

    def stop(self) -> None:
        self._is_running = False
        if self._server_socket:
            try:
                self._server_socket.close()
            except OSError:
                pass
