"""
main.py - Demonstração executável do File Downloader Cliente-Servidor.

Cria um arquivo de teste no servidor, inicia o servidor em streaming,
solicita o arquivo via cliente calculando progresso e validando hash SHA-256.
"""

import hashlib
import os
import shutil
import tempfile
import time
from server import FileServer
from client import FileDownloadClient


def main() -> None:
    print("=" * 65)
    print("DEMONSTRAÇÃO: File Downloader em Streaming (HTTP / Chunks)")
    print("=" * 65)

    temp_dir = tempfile.mkdtemp(prefix="cs_file_download_")
    server_dir = os.path.join(temp_dir, "server_files")
    client_dir = os.path.join(temp_dir, "client_downloads")
    os.makedirs(server_dir, exist_ok=True)
    os.makedirs(client_dir, exist_ok=True)

    try:
        # 1. Cria um arquivo binário de teste de 64 KB no servidor
        filename = "relatorio_financeiro.bin"
        server_file_path = os.path.join(server_dir, filename)
        test_content = os.urandom(64 * 1024)  # 64 KB
        with open(server_file_path, "wb") as f:
            f.write(test_content)

        original_sha = hashlib.sha256(test_content).hexdigest()
        print(f"\n[SERVIDOR] Arquivo gerado no servidor: {filename} ({len(test_content)} bytes)")
        print(f"[SERVIDOR] SHA-256 original: {original_sha}")

        # 2. Inicializa o servidor
        server = FileServer(root_dir=server_dir, port=0)
        server.start()
        port = server.bound_port
        print(f"[SERVIDOR] FileServer ativo na porta {port}")

        # 3. Executa o download com callback de progresso
        client_dest = os.path.join(client_dir, "downloaded_" + filename)
        client = FileDownloadClient(host="127.0.0.1", port=port)

        print("\n[CLIENTE] Iniciando download com leitura em chunks...")

        def progress_callback(received: int, total: int) -> None:
            pct = (received / total) * 100
            print(f"  [Progresso] {received}/{total} bytes ({pct:.1f}%)")

        success, downloaded_sha = client.download_file(
            remote_filename=filename,
            destination_path=client_dest,
            on_progress=progress_callback,
        )

        print(f"\n[CLIENTE] Download concluído com sucesso: {success}")
        print(f"[CLIENTE] SHA-256 do arquivo baixado: {downloaded_sha}")

        # 4. Asserção de integridade
        if success and downloaded_sha == original_sha:
            print("\n✅ SUCESSO: O arquivo baixado é 100% íntegro e idêntico ao original!")
        else:
            print("\n❌ ERRO: Divergência de checksum detectada!")

    finally:
        server.stop()
        shutil.rmtree(temp_dir, ignore_errors=True)
        print("\n[CLEANUP] Diretórios temporários removidos.")
        print("=" * 65)


if __name__ == "__main__":
    main()
