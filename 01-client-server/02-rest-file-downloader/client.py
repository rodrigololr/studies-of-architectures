"""
client.py - Cliente de download HTTP que processa fluxo de dados em streaming.

Recebe os cabeçalhos, processa o Content-Length e lê os dados em pedaços (chunks),
calculando a taxa de progresso e gravando diretamente em disco.
"""

from __future__ import annotations
import hashlib
import socket
from typing import Callable, Optional, Tuple
from protocol import parse_request_line


class FileDownloadClient:
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.chunk_size = 4096

    def download_file(
        self,
        remote_filename: str,
        destination_path: str,
        on_progress: Optional[Callable[[int, int], None]] = None,
    ) -> Tuple[bool, str]:
        """
        Realiza o download em streaming do arquivo.
        Retorna (sucesso, hash_sha256).
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, self.port))

        try:
            # 1. Envia requisição HTTP GET
            request = (
                f"GET /{remote_filename} HTTP/1.1\r\n"
                f"Host: {self.host}:{self.port}\r\n"
                f"Connection: close\r\n\r\n"
            )
            sock.sendall(request.encode("latin-1"))

            # 2. Lê os cabeçalhos HTTP
            header_bytes = b""
            while b"\r\n\r\n" not in header_bytes:
                chunk = sock.recv(512)
                if not chunk:
                    break
                header_bytes += chunk

            if b"\r\n\r\n" not in header_bytes:
                return False, ""

            raw_headers, remaining_body = header_bytes.split(b"\r\n\r\n", 1)
            lines = raw_headers.decode("latin-1").split("\r\n")
            status_line = lines[0]
            status_code = int(status_line.split(" ")[1])

            if status_code != 200:
                return False, ""

            headers = {}
            for line in lines[1:]:
                if ": " in line:
                    k, v = line.split(": ", 1)
                    headers[k.lower()] = v.strip()

            total_bytes = int(headers.get("content-length", 0))
            received_bytes = len(remaining_body)
            hasher = hashlib.sha256()

            # 3. Grava o arquivo localmente em streaming
            with open(destination_path, "wb") as f:
                if remaining_body:
                    f.write(remaining_body)
                    hasher.update(remaining_body)

                while received_bytes < total_bytes:
                    to_read = min(self.chunk_size, total_bytes - received_bytes)
                    chunk = sock.recv(to_read)
                    if not chunk:
                        break
                    f.write(chunk)
                    hasher.update(chunk)
                    received_bytes += len(chunk)
                    if on_progress:
                        on_progress(received_bytes, total_bytes)

            return True, hasher.hexdigest()
        finally:
            sock.close()
