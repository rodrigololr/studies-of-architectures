# ⚙️ Exemplo 03: Mini Compilador e Avaliador de Expressões (Pipes and Filters)

> Implementação da **Arquitetura Pipes and Filters** inspirada no design canônico de compiladores e interpretadores de linguagens de programação, dividida nos estágios de **Análise Léxica (Lexer)**, **Validação Sintática**, **Conversão RPN (Shunting-Yard)** e **Avaliação Aritmética**.

---

## 🎯 1. Cenário do Dia a Dia

Em motores de cálculo de regras de negócio, sistemas contábeis, filtros de busca em SQL ou planilhas (como Excel/Google Sheets), expressões digitadas por usuários precisam ser avaliadas dinamicamente:
- A expressão chega como texto bruto: `"(10 + 20) * 3"`.
- O sistema não pode simplesmente usar `eval()` do Python por graves riscos de injeção de código arbitrário e execução de malware.
- A solução padrão é construir uma esteira em estágios: decompor em tokens atômicos, validar se parênteses estão fechados, reordenar por precedência matemática (*Notação Polonesa Reversa*) e calcular o valor final via pilha.

---

## 💡 2. Justificativa Arquitetural

- **Por que Pipes and Filters aqui?**
  - **Fases Canônicas de Compiladores**: Desde o livro do Dragão (*Compilers: Principles, Techniques, and Tools* de Aho, Lam, Sethi e Ullman), a compilação é ensinada como a aplicação definitiva de Pipes and Filters.
  - **Detecção Pontual de Falhas**: Se o usuário esquecer de fechar um parêntese, o erro é diagnosticado imediatamente no `SyntaxValidatorFilter`, sem gastar processamento tentando converter ou calcular.
  - **Segurança Absoluta**: A avaliação é matemática pura via pilha, sem risco de execução remota de código (*RCE*).

---

## 📊 3. Diagrama do Pipeline de Compilação (Mermaid)

```mermaid
flowchart LR
    Source([Expressão em Texto]) --> P0[Pipe]
    
    subgraph Pipeline ["Pipeline de Compilação"]
        P0 --> F1["LexerFilter<br/>(Gera Tokens)"]
        F1 --> P1[Pipe]
        P1 --> F2["SyntaxValidatorFilter<br/>(Valida Parênteses)"]
        F2 --> P2[Pipe]
        P2 --> F3["ShuntingYardFilter<br/>(Infixo -> RPN)"]
        F3 --> P3[Pipe]
        P3 --> F4["RpnEvaluatorFilter<br/>(Avaliação em Pilha)"]
    end
    
    F4 --> P4[Pipe]
    P4 --> Sink([Resultado Numérico / Erro])

    classDef pipe fill:#e2e8f0,stroke:#64748b,stroke-width:1px,color:#334155;
    classDef filter fill:#dbeafe,stroke:#2563eb,stroke-width:2px,color:#1e40af;
    classDef io fill:#fef3c7,stroke:#d97706,stroke-width:2px,color:#92400e;

    class P0,P1,P2,P3,P4 pipe;
    class F1,F2,F3,F4 filter;
    class Source,Sink io;
```

---

## 📁 4. Estrutura dos Arquivos

```text
03-compiler-lexer-parser-evaluator/
├── README.md                           # Esta documentação
├── main.py                             # Demonstração executável de expressões
├── pipeline/
│   ├── base.py                         # Interface Filter e CompilerPipeline
│   └── context.py                      # Token, TokenType e CompilerContext
└── filters/
    ├── lexer_filter.py                 # Análise léxica e identificação de tokens
    ├── syntax_validator_filter.py      # Checagem de parênteses e operadores soltos
    ├── shunting_yard_filter.py         # Conversão para Notação Polonesa Reversa
    └── evaluator_filter.py             # Computação da pilha RPN
```

---

## 🧼 5. Princípios de Clean Code & SOLID Aplicados

- **Single Responsibility Principle (SRP)**: O Lexer apenas cria tokens; o validador sintático apenas confere gramática; o Shunting-Yard reordena por precedência; o Evaluator faz contas matemáticas.
- **Algoritmo Canônico de Shunting-Yard**: Respeita precedência de operadores (`*` e `/` com peso 2; `+` e `-` com peso 1) e recursão implícita de parênteses.
- **Fail-Safe**: Erros matemáticos como divisão por zero são capturados e transformados em diagnósticos legíveis dentro do contexto sem lançar *crash* no processo principal.

---

## ⚖️ 6. Trade-offs

| Vantagem | Custo / Limitação |
|---|---|
| Segurança extrema contra injeção de código e alta manutenibilidade | Requer modelagem de tokens e estruturas de dados intermediárias. |
| Fácil suporte a novas operações (ex: potências `^`, módulo `%`) | O encadeamento sequencial adiciona passos a mais para cálculos simples. |

---

## 🚀 7. Como Executar

```bash
# A partir desta pasta:
python3 main.py
```
