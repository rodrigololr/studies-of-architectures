# 🎙️ Exemplo 06: Pré-Processamento e Transcrição de Áudio (Pipes and Filters)

> Implementação da **Arquitetura Pipes and Filters** para uma esteira de ingestão multimídia (*Audio Processing & Speech-to-Text Pipeline*), demonstrando validação de taxa de amostragem, remoção de silêncio para economia de tokens, redução de ruído espectral, fatiamento temporal (*chunking*) e transcrição fonética.

---

## 🎯 1. Cenário do Dia a Dia

Em sistemas de inteligência artificial de voz e transcrição (como OpenAI Whisper, Google Speech-to-Text ou gravação de chamadas de SAC):
1. Usuários gravam mensagens em formatos variados com ruído de fundo (carros passando, ventilador) e longos silêncios no início e no final.
2. Mandar o áudio cru diretamente para a API de IA gera custos desnecessários de tokens e pode causar erros de alucinação do modelo.
3. A esteira aplica filtros especializados: valida a frequência mínima para inteligibilidade (mínimo de 8.000 Hz), apara os segundos mortos de silêncio, aplica filtro passa-baixa de redução de ruído, fatia áudios longos em pedaços de 20 segundos e distribui para transcrição.

---

## 💡 2. Justificativa Arquitetural

- **Por que Pipes and Filters aqui?**
  - **Fases Especializadas de DSP (Digital Signal Processing)**: Cada transformação sonora é matematicamente isolada em sua própria classe (`SilenceTrimmerFilter`, `NoiseReductionFilter`, `AudioChunkerFilter`).
  - **Eficiência de Custo de Nuvem**: Ao podar 3,5 segundos de silêncio de milhões de áudios diários, a esteira economiza milhares de dólares em tempo de máquina de IA.
  - **Fatiamento para Paralelismo**: O filtro de *chunking* viabiliza que múltiplos workers transcrevam os pedaços de áudio em paralelo antes de concatenar o resultado final.

---

## 📊 3. Diagrama do Pipeline de Áudio (Mermaid)

```mermaid
flowchart LR
    Source([Arquivo de Áudio Bruto]) --> P0[Pipe]
    
    subgraph Pipeline ["Pipeline de Áudio & IA"]
        P0 --> F1["AudioHeaderValidator<br/>(Min 8000 Hz)"]
        F1 --> P1[Pipe]
        P1 --> F2["SilenceTrimmerFilter<br/>(Apara Silêncio)"]
        F2 --> P2[Pipe]
        P2 --> F3["NoiseReductionFilter<br/>(Subtração de Ruído)"]
        F3 --> P3[Pipe]
        P3 --> F4["AudioChunkerFilter<br/>(Chunks de 20s)"]
        F4 --> P4[Pipe]
        P4 --> F5["SpeechToTextFilter<br/>(Transcrição Fonética)"]
    end
    
    F5 --> P5[Pipe]
    P5 --> Sink([Texto Transcrito Consolidado])

    classDef pipe fill:#e2e8f0,stroke:#64748b,stroke-width:1px,color:#334155;
    classDef filter fill:#dbeafe,stroke:#2563eb,stroke-width:2px,color:#1e40af;
    classDef io fill:#fef3c7,stroke:#d97706,stroke-width:2px,color:#92400e;

    class P0,P1,P2,P3,P4,P5 pipe;
    class F1,F2,F3,F4,F5 filter;
    class Source,Sink io;
```

---

## 📁 4. Estrutura dos Arquivos

```text
06-audio-transcription-normalizer/
├── README.md                           # Esta documentação
├── main.py                             # Execução do pipeline sobre gravações de áudio
├── pipeline/
│   ├── base.py                         # Interface Filter e AudioPipeline
│   └── context.py                      # AudioContext e AudioChunk
└── filters/
    ├── header_validator_filter.py      # Verificação de formatos e Hertz mínimos
    ├── silence_trimmer_filter.py       # Remoção de segundos mortos
    ├── noise_reducer_filter.py         # Filtro de ruído de fundo
    ├── chunker_filter.py               # Divisão em intervalos de tempo
    └── transcriber_filter.py           # Transcrição fonética e junção
```

---

## 🧼 5. Princípios de Clean Code & SOLID Aplicados

- **Single Responsibility Principle (SRP)**: Cada filtro realiza apenas uma operação sonora no fluxo.
- **Fail-Fast**: Áudios corrompidos ou com taxa de amostragem muito baixa (ex: 4.000 Hz) são rejeitados no primeiro filtro antes de qualquer processamento de ruído ou transcrição.
- **Estruturas Imutáveis de Fatiamento**: A classe `AudioChunk` armazena os limites de tempo de início e fim (`start_second`, `end_second`) com precisão decimal.

---

## ⚖️ 6. Trade-offs

| Vantagem | Custo / Limitação |
|---|---|
| Redução substancial de custo de APIs de inteligência artificial de voz | A fragmentação em chunks exige algoritmo de sobreposição de bordas (*overlap*) para não cortar palavras ao meio. |
| Altíssima testabilidade de cada estágio de processamento | Arquivos gigantescos podem exigir streaming de bytes em disco em vez de buffers em memória. |

---

## 🚀 7. Como Executar

```bash
# A partir desta pasta:
python3 main.py
```
