"""
main.py - Demonstração executável do Pipeline de Mídia (Pipes and Filters).

Monta os estágios de validação, expurgo de dados de GPS (privacidade),
redimensionamento, marca d'água e compressão para entrega em CDN.
"""

from pipeline.base import ImagePipeline
from pipeline.context import ImagePayload, ImageMetadata
from filters.format_validator_filter import FormatValidatorFilter
from filters.exif_privacy_filter import ExifPrivacyFilter
from filters.resolution_resize_filter import ResolutionResizeFilter
from filters.watermark_filter import WatermarkFilter
from filters.compression_filter import CompressionOptimizationFilter


def main() -> None:
    print("=" * 82)
    print("DEMONSTRAÇÃO: Pipes and Filters (Pipeline de Ingestão e Processamento de Mídia)")
    print("=" * 82)

    # 1. Montagem do Pipeline fluente
    pipeline = ImagePipeline()
    pipeline.add_filter(FormatValidatorFilter())
    pipeline.add_filter(ExifPrivacyFilter())
    pipeline.add_filter(ResolutionResizeFilter(max_width=1920, max_height=1080))
    pipeline.add_filter(WatermarkFilter(watermark_text="© 2026 Estudos de Arquitetura"))
    pipeline.add_filter(CompressionOptimizationFilter(compression_ratio=0.55))

    # 2. Imagens de entrada simuladas
    test_images = [
        # Imagem 1: Foto JPEG de 4000x3000 tirada de celular com GPS residencial
        ImagePayload(
            filename="foto_ferias_iphone.jpeg",
            file_format="JPEG",
            raw_size_bytes=6_500_000,  # ~6.5 MB
            width=4000,
            height=3000,
            metadata=ImageMetadata(
                camera_model="iPhone 15 Pro",
                gps_coordinates="-23.550520, -46.633308",  # Dado sensível!
                created_at="2026-09-15 14:30:00",
            ),
        ),
        # Imagem 2: Banner institucional PNG já em tamanho padrão
        ImagePayload(
            filename="banner_institucional.png",
            file_format="PNG",
            raw_size_bytes=1_200_000,  # ~1.2 MB
            width=1200,
            height=630,
            metadata=ImageMetadata(created_at="2026-10-01 10:00:00"),
        ),
        # Imagem 3: Arquivo malicioso com extensão executável disfarçada
        ImagePayload(
            filename="foto_documento.php.jpg",
            file_format="JPG",
            raw_size_bytes=45_000,
            width=800,
            height=600,
            metadata=ImageMetadata(),
        ),
    ]

    print("\n--- Submetendo Imagens ao Pipeline ---")

    for img in test_images:
        print(f"\n[ENTRADA] Arquivo: {img.filename} ({img.width}x{img.height}, {img.raw_size_bytes / 1024:.1f} KB)")
        if img.metadata.gps_coordinates:
            print(f"          ⚠️ Metadados EXIF presentes: GPS = {img.metadata.gps_coordinates}")

        result: ImagePayload = pipeline.execute(img)

        if result.is_valid:
            print("  ✅ SUCESSO NO PROCESSAMENTO:")
            print(f"     • Resolução Final:    {result.width}x{result.height}")
            print(f"     • Tamanho Otimizado:  {result.raw_size_bytes / 1024:.1f} KB (Comprimido)")
            print(f"     • GPS Preservado:     {result.metadata.gps_coordinates} (Removido com sucesso)")
            print(f"     • Marca d'Água:       {result.watermark_text}")
        else:
            print(f"  ❌ REJEITADO NO PIPELINE: {result.rejection_reason}")

    print("\n" + "=" * 82)


if __name__ == "__main__":
    main()
