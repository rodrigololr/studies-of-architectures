# 🖼️ Exemplo 02: Processamento de Imagens e Metadados (Pipes and Filters)

> Implementação da **Arquitetura Pipes and Filters** para uma esteira de ingestão de mídia (*Media Processing Pipeline*), demonstrando validação de segurança de arquivos, expurgo de geolocalização EXIF para conformidade LGPD/GDPR, redimensionamento dimensional, aplicação de marca d'água e compressão de bytes.

---

## 🎯 1. Cenário do Dia a Dia

Plataformas de redes sociais, portais imobiliários e e-commerces (como Mercado Livre, Instagram, Airbnb) recebem uploads contínuos de fotos tiradas por usuários:
1. Fotos tiradas por smartphones contêm metadados EXIF com coordenadas exatas de GPS (latitude/longitude da residência do usuário), gerando sérios riscos de segurança e violação de leis de privacidade (LGPD/GDPR).
2. Arquivos podem conter extensões duplas maliciosas (ex: `foto.php.jpg`) para tentar executar código remoto no servidor.
3. Fotos em 4K/8K sobrecarregam servidores e devem ser redimensionadas preservando a proporção de aspecto (*aspect ratio*).
4. O portal precisa aplicar a marca d'água de proteção autoral e comprimir a imagem antes de enviá-la para o bucket S3 e CDNs.

---

## 💡 2. Justificativa Arquitetural

- **Por que Pipes and Filters aqui?**
  - **Filtros Isolados**: O filtro que apaga dados de GPS (`ExifPrivacyFilter`) não sabe nada sobre redimensionamento; o filtro de redimensionamento (`ResolutionResizeFilter`) não sabe nada sobre compressão.
  - **Eficiência e Proteção Precoce**: Se o arquivo for malicioso, o primeiro filtro (`FormatValidatorFilter`) aborta o processamento imediatamente, economizando CPU e memória que seriam desperdiçados tentando redimensionar um script invasor.
  - **Extensibilidade**: Plugar novos filtros (ex: filtro de desfoque de rostos ou moderação de conteúdo adulto com IA) não exige refatoração da esteira.

---

## 📊 3. Diagrama do Pipeline (Mermaid)

```mermaid
flowchart LR
    Source([Upload de Imagem Bruta]) --> P0[Pipe]
    
    subgraph Pipeline ["Pipeline de Ingestão de Mídia"]
        P0 --> F1["FormatValidatorFilter<br/>(Bloqueia .php/.exe)"]
        F1 --> P1[Pipe]
        P1 --> F2["ExifPrivacyFilter<br/>(Remove GPS / Câmera)"]
        F2 --> P2[Pipe]
        P2 --> F3["ResolutionResizeFilter<br/>(Max 1920x1080)"]
        F3 --> P3[Pipe]
        P3 --> F4["WatermarkFilter<br/>(Aplica Copyright)"]
        F4 --> P4[Pipe]
        P4 --> F5["CompressionFilter<br/>(Reduz Bytes em 45%)"]
    end
    
    F5 --> P5[Pipe]
    P5 --> Valid{"Válido?"}
    Valid -- "Sim" --> SinkCDN([Armazenamento CDN / S3])
    Valid -- "Não" --> SinkDrop([Descarte com Log de Erro])

    classDef pipe fill:#e2e8f0,stroke:#64748b,stroke-width:1px,color:#334155;
    classDef filter fill:#dbeafe,stroke:#2563eb,stroke-width:2px,color:#1e40af;
    classDef io fill:#fef3c7,stroke:#d97706,stroke-width:2px,color:#92400e;

    class P0,P1,P2,P3,P4,P5 pipe;
    class F1,F2,F3,F4,F5 filter;
    class Source,SinkCDN,SinkDrop io;
```

---

## 📁 4. Estrutura dos Arquivos

```text
02-image-metadata-and-watermark/
├── README.md                           # Esta documentação
├── main.py                             # Execução do pipeline sobre lote de imagens
├── pipeline/
│   ├── base.py                         # Interface Filter e ImagePipeline
│   └── context.py                      # ImagePayload e ImageMetadata
└── filters/
    ├── format_validator_filter.py      # Bloqueio de extensões maliciosas
    ├── exif_privacy_filter.py          # Expurgador de GPS e privacidade
    ├── resolution_resize_filter.py     # Redimensionamento proporcional
    ├── watermark_filter.py             # Aplicação de marca d'água de copyright
    └── compression_filter.py           # Otimização de bytes para CDN
```

---

## 🧼 5. Princípios de Clean Code & SOLID Aplicados

- **Open/Closed Principle (OCP)**: O pipeline está fechado para alteração de seu mecanismo central de encadeamento, mas aberto para adição de novos filtros de imagem.
- **Privacy by Design**: A remoção de geolocalização e modelo de aparelho do usuário é implementada como uma etapa determinística mandatória do fluxo.
- **Fail-Fast**: A verificação de extensão suspeita no início impede que arquivos potencialmente nocivos atinjam filtros subsequentes.

---

## ⚖️ 6. Trade-offs

| Vantagem | Custo / Limitação |
|---|---|
| Pipeline extensível e autoexplicativo | Cada estágio lê e reescreve propriedades do objeto de contexto. |
| Fácil paralelização por workers | Manipulação pesada de matrizes reais de pixels (ex: com Pillow ou OpenCV) exige cuidado com consumo de CPU. |

---

## 🚀 7. Como Executar

```bash
# A partir desta pasta:
python3 main.py
```
