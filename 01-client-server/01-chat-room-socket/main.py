"""
main.py - Demonstração executável do Chat Room Cliente-Servidor.

Executa o servidor e simula dois clientes (Alice e Bob) conversando
e recebendo eventos em tempo real, finalizando de forma limpa.
"""

import time
from protocol import Message
from server import ChatServer
from client import ChatClient


def main() -> None:
    print("=" * 65)
    print("DEMONSTRAÇÃO: Arquitetura Cliente-Servidor (Chat Room TCP)")
    print("=" * 65)

    # 1. Inicia o Servidor em porta efêmera (port=0 deixa o SO escolher uma porta livre)
    server = ChatServer(host="127.0.0.1", port=0)
    server.start()
    server_port = server.bound_port
    print(f"\n[SERVIDOR] ChatServer ouvindo em 127.0.0.1:{server_port}")

    # 2. Configura callbacks de recebimento dos clientes
    def on_alice_msg(msg: Message) -> None:
        print(f"  [Alice View] <{msg.sender}>: {msg.content}")

    def on_bob_msg(msg: Message) -> None:
        print(f"  [Bob View]   <{msg.sender}>: {msg.content}")

    # 3. Conecta Cliente Alice
    print("\n[CLIENTE 1] Alice conectando...")
    alice = ChatClient("Alice", port=server_port, on_message_received=on_alice_msg)
    alice.connect()
    time.sleep(0.1)

    # 4. Conecta Cliente Bob
    print("\n[CLIENTE 2] Bob conectando...")
    bob = ChatClient("Bob", port=server_port, on_message_received=on_bob_msg)
    bob.connect()
    time.sleep(0.1)

    # 5. Troca de Mensagens
    print("\n--- Troca de Mensagens em Tempo Real ---")
    alice.send_chat("Olá Bob! Tudo bem?")
    time.sleep(0.1)

    bob.send_chat("Oi Alice! Tudo ótimo por aqui e por aí?")
    time.sleep(0.1)

    alice.send_chat("Tudo certo! Demonstrando arquitetura cliente-servidor em Python.")
    time.sleep(0.1)

    # 6. Desconexão graciosa
    print("\n[CLIENTE] Bob desconectando...")
    bob.disconnect()
    time.sleep(0.1)

    print("\n[CLIENTE] Alice desconectando...")
    alice.disconnect()
    time.sleep(0.1)

    # 7. Encerramento do Servidor
    print("\n[SERVIDOR] Encerrando ChatServer...")
    server.stop()
    print("[FIM] Demonstração concluída com sucesso e recursos liberados!")
    print("=" * 65)


if __name__ == "__main__":
    main()
