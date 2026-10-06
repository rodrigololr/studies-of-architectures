"""
main.py - Composition Root e Demonstração do Exemplo 06.
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core.service import DocumentManagementService
from adapters.secondary.aws_s3_storage_adapter import AwsS3StorageAdapter
from adapters.secondary.local_disk_storage_adapter import LocalDiskStorageAdapter
from adapters.secondary.google_cloud_storage_adapter import GoogleCloudStorageAdapter
from adapters.secondary.clamav_antivirus_adapter import ClamAvAntivirusAdapter
from adapters.secondary.in_memory_metadata_adapter import InMemoryDocumentMetadataAdapter
from adapters.primary.file_upload_http_controller import FileUploadHttpController
from adapters.primary.batch_folder_watcher_adapter import BatchFolderWatcherAdapter


def main() -> None:
    print("=" * 80)
    print(" HEXAGONAL ARCHITECTURE - EXEMPLO 06: FILE PROCESSING & MULTI-CLOUD STORAGE")
    print("=" * 80)

    # 1. Adaptadores Secundários (Driven)
    s3_storage = AwsS3StorageAdapter(bucket_name="corporativo-contratos-prod")
    gcs_storage = GoogleCloudStorageAdapter(bucket_name="docs-archive-gcs")
    local_storage = LocalDiskStorageAdapter(base_mount_path="/mnt/storage_backup")

    clamav = ClamAvAntivirusAdapter()
    metadata_repo = InMemoryDocumentMetadataAdapter()

    # 2. Núcleo da Aplicação (Core / Hexágono) conectado inicialmente ao AWS S3
    service = DocumentManagementService(
        storage_port=s3_storage,
        antivirus_port=clamav,
        metadata_repo=metadata_repo,
    )

    # 3. Adaptadores Primários (Driver)
    http_controller = FileUploadHttpController(
        upload_use_case=service,
        download_use_case=service,
    )
    folder_watcher = BatchFolderWatcherAdapter(upload_use_case=service)

    print("\n--- CENÁRIO 1: Upload de Contrato em PDF para o AWS S3 via API HTTP ---")
    contract_bytes = b"%PDF-1.4 ... CONTRATO DE PRESTACAO DE SERVICOS TI 2026 ... %%EOF"
    status, res = http_controller.handle_post_file(
        filename="contrato_tech_2026.pdf",
        content_bytes=contract_bytes,
        mime_type="application/pdf",
        user_id="usr-juridico-10",
    )
    print(f"Status HTTP: {status}")
    print(json.dumps(res, indent=2, ensure_ascii=False))
    doc_id_1 = res["document_id"]

    print("\n--- CENÁRIO 2: Download do Arquivo e Verificação Criptográfica de Integridade ---")
    status, res_down = http_controller.handle_get_file(doc_id_1)
    print(f"Status HTTP: {status} | Arquivo: {res_down['filename']} | SHA256: {res_down['sha256'][:16]}...")
    print(f"Preview do conteúdo: \"{res_down['content_preview']}\"")

    print("\n--- CENÁRIO 3: Troca Dinâmica de Armazenamento para Google Cloud Storage (GCS) ---")
    # Trocamos o adaptador plugado na porta BlobStoragePort sem modificar o serviço ou o domínio!
    service.storage_port = gcs_storage
    print("[Configuração] Provedor de Blob Storage alterado em tempo de execução para Google Cloud Storage.")

    report_bytes = b"id,setor,faturamento\n1,Vendas,150000.00\n2,Marketing,80000.00"
    status, res = http_controller.handle_post_file(
        filename="relatorio_financeiro.csv",
        content_bytes=report_bytes,
        mime_type="text/csv",
        user_id="usr-financeiro-02",
    )
    print(f"Status HTTP: {status}")
    print(f"Documento gravado no GCS: {res['storage_uri']} (Provedor: {res['provider']})")

    print("\n--- CENÁRIO 4: Bloqueio Preventivo por Scanner Antivírus (ClamAV Driven Port) ---")
    malicious_bytes = b"Normal header... EICAR-STANDARD-ANTIVIRUS-TEST-FILE ... footer"
    status, res = http_controller.handle_post_file(
        filename="planilha_suspeita.csv",
        content_bytes=malicious_bytes,
        mime_type="text/csv",
        user_id="usr-desconhecido",
    )
    print(f"Status HTTP: {status} | Resposta: {res}")

    print("\n--- CENÁRIO 5: Rejeição por Tipo de Arquivo Proibido (.exe / scripts) ---")
    script_bytes = b"#!/bin/bash\nrm -rf /"
    status, res = http_controller.handle_post_file(
        filename="script_perigoso.sh",
        content_bytes=script_bytes,
        mime_type="application/x-sh",
        user_id="usr-hacker",
    )
    print(f"Status HTTP: {status} | Resposta: {res}")

    print("\n--- CENÁRIO 6: Ingestão em Lote via Adaptador Batch Folder Watcher ---")
    batch_files = [
        ("nota_fiscal_01.pdf", b"%PDF-1.4 NF01 ...", "application/pdf"),
        ("nota_fiscal_02.pdf", b"%PDF-1.4 NF02 ...", "application/pdf"),
        ("instalador.exe", b"MZ...", "application/x-dosexec"),  # Será rejeitado
    ]
    watcher_logs = folder_watcher.ingest_batch(batch_files, operator_id="cron-watcher-job")
    for log in watcher_logs:
        print(log)

    print("\n--- CENÁRIO 7: Auditoria de Documentos Persistidos no Repositório ---")
    docs = metadata_repo.list_all()
    print(f"Total de documentos indexados: {len(docs)}")
    for d in docs:
        print(f" -> [{d.created_at.strftime('%H:%M:%S')}] {d.original_filename:26} | Provedor: {d.storage_provider.value:22} | URI: {d.storage_path}")

    print("\n" + "=" * 80)
    print(" Exemplo 06 finalizado com sucesso!")
    print("=" * 80)


if __name__ == "__main__":
    main()
