"""
client.py - Cliente RPC com Stub e Encapsulamento de Erros.

Permite invocar métodos remotos com sintaxe similar a uma chamada de função local.
"""

from __future__ import annotations
import socket
import uuid
from typing import Any
from protocol import RpcRequest, RpcResponse


class RemoteProcedureError(Exception):
    """Exceção levantada quando o servidor retorna erro na execução remota."""
    pass


class RpcClient:
    def __init__(self, auth_token: str, host: str = "127.0.0.1", port: int = 8080) -> None:
        self.auth_token = auth_token
        self.host = host
        self.port = port

    def call(self, method: str, **params: Any) -> Any:
        """Invoca o procedimento remoto no servidor e retorna o resultado."""
        req_id = str(uuid.uuid4())[:8]
        request = RpcRequest(
            request_id=req_id,
            auth_token=self.auth_token,
            method=method,
            params=params,
        )

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3.0)
        sock.connect((self.host, self.port))

        try:
            sock.sendall(request.serialize())

            buffer = ""
            while "\n" not in buffer:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                buffer += chunk.decode("utf-8")

            line, _ = buffer.split("\n", 1)
            response = RpcResponse.deserialize(line)

            if not response or response.request_id != req_id:
                raise RemoteProcedureError("Resposta RPC inválida ou corrompida")

            if not response.success:
                raise RemoteProcedureError(response.error or "Erro remoto desconhecido")

            return response.result

        finally:
            sock.close()
