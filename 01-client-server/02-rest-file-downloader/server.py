"""
server.py - Servidor HTTP que transmite arquivos em streaming por chunks.

Evita carregar o arquivo inteiro na memória RAM, transmitindo blocos
de tamanho fixo diretamente para o socket do cliente conectado.
"""

from __future__ import annotations
import os
import socket
import threading
from typing import Optional
from protocol import HttpResponseHeaders, parse_request_line


class FileServer:
    def __init__(self, root_dir: str, host: str = "127.0.0.1", port: int = 0) -> None:
        self.root_dir = root_dir
        self.host = host
        self.port = port
        self.chunk_size = 4096  # 4 KB por chunk
        self._server_socket: Optional[socket.socket] = None
        self._is_running = False
        self._accept_thread: Optional[threading.Thread] = None

    @property
    def bound_port(self) -> int:
        if self._server_socket:
            return self._server_socket.getsockname()[1]
        return self.port

    def start(self) -> None:
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.bind((self.host, self.port))
        self._server_socket.listen(5)
        self._is_running = True

        self._accept_thread = threading.Thread(target=self._accept_loop, daemon=True)
        self._accept_thread.start()

    def _accept_loop(self) -> None:
        while self._is_running and self._server_socket:
            try:
                client_sock, _ = self._server_socket.accept()
                threading.Thread(
                    target=self._handle_request, args=(client_sock,), daemon=True
                ).start()
            except OSError:
                break

    def _handle_request(self, client_sock: socket.socket) -> None:
        try:
            raw_data = client_sock.recv(4096).decode("latin-1")
            method, path, _ = parse_request_line(raw_data)

            if method != "GET":
                resp = HttpResponseHeaders(405, "Method Not Allowed", {"Content-Length": "0"})
                client_sock.sendall(resp.serialize())
                return

            filename = path.lstrip("/")
            file_path = os.path.join(self.root_dir, filename)

            # Prevenção contra Directory Traversal
            normalized_path = os.path.abspath(file_path)
            normalized_root = os.path.abspath(self.root_dir)
            if not normalized_path.startswith(normalized_root) or not os.path.isfile(normalized_path):
                not_found_msg = b"404 Arquivo Nao Encontrado\n"
                resp = HttpResponseHeaders(
                    404,
                    "Not Found",
                    {"Content-Length": str(len(not_found_msg)), "Content-Type": "text/plain"},
                )
                client_sock.sendall(resp.serialize() + not_found_msg)
                return

            file_size = os.path.getsize(normalized_path)
            headers = HttpResponseHeaders(
                status_code=200,
                reason="OK",
                headers={
                    "Content-Length": str(file_size),
                    "Content-Type": "application/octet-stream",
                },
            )
            client_sock.sendall(headers.serialize())

            # Streaming em chunks de 4KB
            with open(normalized_path, "rb") as f:
                while chunk := f.read(self.chunk_size):
                    client_sock.sendall(chunk)

        except Exception:
            pass
        finally:
            try:
                client_sock.close()
            except OSError:
                pass

    def stop(self) -> None:
        self._is_running = False
        if self._server_socket:
            try:
                self._server_socket.close()
            except OSError:
                pass
