"""
client.py - Cliente TCP para comunicação com o Chat Room.

Responsabilidade:
- Conectar ao socket do servidor.
- Enviar mensagens respeitando o enquadramento do protocolo.
- Escutar mensagens assincronamente através de thread dedicada.
- Fornecer callback para a aplicação cliente processar eventos recebidos.
"""

from __future__ import annotations
from datetime import datetime
import socket
import threading
from typing import Callable, Optional
from protocol import Message, MessageType


class ChatClient:
    def __init__(
        self,
        username: str,
        host: str = "127.0.0.1",
        port: int = 8080,
        on_message_received: Optional[Callable[[Message], None]] = None,
    ) -> None:
        self.username = username
        self.host = host
        self.port = port
        self.on_message_received = on_message_received
        self._sock: Optional[socket.socket] = None
        self._is_running = False
        self._receive_thread: Optional[threading.Thread] = None

    def connect(self) -> None:
        """Abre conexão com o servidor e envia mensagem JOIN."""
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.connect((self.host, self.port))
        self._is_running = True

        self._receive_thread = threading.Thread(
            target=self._listen_loop,
            daemon=True,
            name=f"Listener-{self.username}",
        )
        self._receive_thread.start()

        join_msg = Message(
            message_type=MessageType.JOIN,
            sender=self.username,
            content="",
            timestamp=datetime.now().strftime("%H:%M:%S"),
        )
        self._send_raw(join_msg.serialize())

    def send_chat(self, text: str) -> None:
        """Envia mensagem de texto convencional."""
        if not self._is_running or not self._sock:
            raise RuntimeError("Cliente não está conectado.")

        msg = Message(
            message_type=MessageType.CHAT,
            sender=self.username,
            content=text,
            timestamp=datetime.now().strftime("%H:%M:%S"),
        )
        self._send_raw(msg.serialize())

    def _send_raw(self, payload: bytes) -> None:
        if self._sock:
            self._sock.sendall(payload)

    def _listen_loop(self) -> None:
        """Escuta continuamente dados vindos do servidor."""
        buffer = ""
        while self._is_running and self._sock:
            try:
                data = self._sock.recv(4096)
                if not data:
                    break

                buffer += data.decode("utf-8")
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    message = Message.deserialize(line)
                    if message and self.on_message_received:
                        self.on_message_received(message)
            except OSError:
                break

    def disconnect(self) -> None:
        """Encerra a conexão cordialmente com o servidor."""
        if not self._is_running:
            return

        self._is_running = False
        if self._sock:
            try:
                leave_msg = Message(
                    message_type=MessageType.LEAVE,
                    sender=self.username,
                    content="",
                )
                self._sock.sendall(leave_msg.serialize())
                self._sock.close()
            except OSError:
                pass
