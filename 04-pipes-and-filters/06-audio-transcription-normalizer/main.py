"""
main.py - Demonstração executável do Pipeline de Transcrição de Áudio (Pipes and Filters).

Encadeia validação de cabeçalho, corte de silêncio, redução de ruído,
chunking temporal e transcrição fonética simulada.
"""

from pipeline.base import AudioPipeline
from pipeline.context import AudioContext
from filters.header_validator_filter import AudioHeaderValidatorFilter
from filters.silence_trimmer_filter import SilenceTrimmerFilter
from filters.noise_reducer_filter import NoiseReductionFilter
from filters.chunker_filter import AudioChunkerFilter
from filters.transcriber_filter import SpeechToTextFilter


def main() -> None:
    print("=" * 82)
    print("DEMONSTRAÇÃO: Pipes and Filters (Pipeline de Pré-Processamento e Transcrição de Áudio)")
    print("=" * 82)

    # 1. Montagem do Pipeline
    pipeline = AudioPipeline()
    pipeline.add_filter(AudioHeaderValidatorFilter())
    pipeline.add_filter(SilenceTrimmerFilter(simulated_trim_seconds=3.5))
    pipeline.add_filter(NoiseReductionFilter())
    pipeline.add_filter(AudioChunkerFilter(max_chunk_duration=20.0))
    pipeline.add_filter(SpeechToTextFilter())

    # 2. Arquivos de áudio submetidos ao pipeline
    audio_files = [
        # Áudio 1: Reunião longa de 48 segundos com taxa de amostragem padrão de 44.100 Hz
        AudioContext(
            audio_id="AUD-001",
            filename="reuniao_sprint_planejamento.wav",
            audio_format="WAV",
            sample_rate_hz=44100,
            duration_seconds=48.0,
        ),
        # Áudio 2: Mensagem curta de voz de 12 segundos em MP3 (16.000 Hz)
        AudioContext(
            audio_id="AUD-002",
            filename="recado_cliente_suporte.mp3",
            audio_format="MP3",
            sample_rate_hz=16000,
            duration_seconds=12.0,
        ),
        # Áudio 3: Arquivo degradado com taxa de 4.000 Hz (ininteligível para transcrição)
        AudioContext(
            audio_id="AUD-003",
            filename="radio_antigo_corrompido.wav",
            audio_format="WAV",
            sample_rate_hz=4000,
            duration_seconds=30.0,
        ),
    ]

    print("\n--- Submetendo Gravações de Áudio ao Pipeline de IA ---")

    for audio in audio_files:
        print(f"\n[ENTRADA] Arquivo: {audio.filename} ({audio.audio_format}, {audio.sample_rate_hz} Hz, {audio.duration_seconds}s)")
        result: AudioContext = pipeline.execute(audio)

        if result.is_valid:
            print("  ✅ PROCESSAMENTO CONCLUÍDO COM SUCESSO:")
            print(f"     • Silêncio Podado:      {result.silence_trimmed_seconds}s")
            print(f"     • Duração Efetiva:      {result.effective_duration}s")
            print(f"     • Ruído Reduzido:       {result.noise_reduced}")
            print(f"     • Chunks Criados:       {len(result.chunks)} segmento(s)")
            for ch in result.chunks:
                print(f"        - Chunk #{ch.chunk_index}: [{ch.start_second:.1f}s a {ch.end_second:.1f}s]")
            print(f"     • Transcrição Final:    \"{result.final_transcript}\"")
        else:
            print(f"  ❌ REJEITADO NO PIPELINE: {result.rejection_reason}")

    print("\n" + "=" * 82)


if __name__ == "__main__":
    main()
