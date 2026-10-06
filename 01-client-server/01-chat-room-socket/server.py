"""
server.py - Servidor multithreaded de Chat Room sobre TCP.

Responsabilidade:
- Aguardar novas conexões de clientes (bind/listen).
- Manter registro de clientes conectados.
- Fazer broadcast de mensagens para todos os participantes.
- Isolar falhas de clientes desconectados sem derrubar o servidor.
"""

from __future__ import annotations
from datetime import datetime
import socket
import threading
from typing import Dict
from protocol import Message, MessageType


class ChatServer:
    def __init__(self, host: str = "127.0.0.1", port: int = 0) -> None:
        self.host = host
        self.port = port
        self._server_socket: socket.socket | None = None
        self._is_running = False
        self._clients_lock = threading.Lock()
        # Mapeia connection -> username
        self._clients: Dict[socket.socket, str] = {}
        self._threads: list[threading.Thread] = []

    @property
    def bound_port(self) -> int:
        """Retorna a porta real onde o servidor está ouvindo."""
        if self._server_socket:
            return self._server_socket.getsockname()[1]
        return self.port

    def start(self) -> None:
        """Inicializa o socket e entra em escuta passiva."""
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.bind((self.host, self.port))
        self._server_socket.listen(10)
        self._is_running = True

        accept_thread = threading.Thread(target=self._accept_loop, daemon=True, name="AcceptLoop")
        accept_thread.start()
        self._threads.append(accept_thread)

    def _accept_loop(self) -> None:
        """Loop principal de aceitação de conexões de clientes."""
        while self._is_running and self._server_socket:
            try:
                client_sock, _ = self._server_socket.accept()
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_sock,),
                    daemon=True,
                    name=f"ClientHandler-{client_sock.fileno()}",
                )
                client_thread.start()
                self._threads.append(client_thread)
            except OSError:
                break

    def _handle_client(self, client_sock: socket.socket) -> None:
        """Trata o ciclo de vida da comunicação de um cliente específico."""
        buffer = ""
        username = "Anônimo"

        try:
            while self._is_running:
                data = client_sock.recv(4096)
                if not data:
                    break

                buffer += data.decode("utf-8")
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    message = Message.deserialize(line)
                    if not message:
                        continue

                    if message.message_type == MessageType.JOIN:
                        username = message.sender
                        with self._clients_lock:
                            self._clients[client_sock] = username
                        self._broadcast(
                            Message(
                                message_type=MessageType.SYSTEM,
                                sender="Servidor",
                                content=f"'{username}' entrou na sala.",
                                timestamp=datetime.now().strftime("%H:%M:%S"),
                            )
                        )

                    elif message.message_type == MessageType.CHAT:
                        self._broadcast(
                            Message(
                                message_type=MessageType.CHAT,
                                sender=username,
                                content=message.content,
                                timestamp=datetime.now().strftime("%H:%M:%S"),
                            )
                        )

                    elif message.message_type == MessageType.LEAVE:
                        return
        except Exception:
            pass
        finally:
            self._disconnect_client(client_sock, username)

    def _disconnect_client(self, client_sock: socket.socket, username: str) -> None:
        """Remove o cliente e avisa os demais participantes."""
        with self._clients_lock:
            if client_sock in self._clients:
                del self._clients[client_sock]
        try:
            client_sock.close()
        except OSError:
            pass

        if username != "Anônimo":
            self._broadcast(
                Message(
                    message_type=MessageType.SYSTEM,
                    sender="Servidor",
                    content=f"'{username}' saiu da sala.",
                    timestamp=datetime.now().strftime("%H:%M:%S"),
                )
            )

    def _broadcast(self, message: Message) -> None:
        """Envia mensagem para todos os clientes conectados."""
        data = message.serialize()
        with self._clients_lock:
            active_clients = list(self._clients.keys())

        for client in active_clients:
            try:
                client.sendall(data)
            except OSError:
                pass

    def stop(self) -> None:
        """Encerra o servidor e fecha todas as conexões."""
        self._is_running = False
        if self._server_socket:
            try:
                self._server_socket.close()
            except OSError:
                pass

        with self._clients_lock:
            for sock in list(self._clients.keys()):
                try:
                    sock.close()
                except OSError:
                    pass
            self._clients.clear()
