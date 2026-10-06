# 🛍️ Exemplo 05: Pipeline de Validação de Pedidos E-commerce (Pipes and Filters)

> Implementação da **Arquitetura Pipes and Filters** para esteiras transacionais de checkout de e-commerce, demonstrando **Interrupção Precoce (*Short-Circuiting*)**, análise de risco antifraude, conferência de estoque de armazém e cálculo tributário interestadual (ICMS).

---

## 🎯 1. Cenário do Dia a Dia

Antes de disparar uma chamada onerosa de cobrança no cartão de crédito do cliente em um e-commerce:
1. O pedido deve passar por uma série de portões de qualidade e conformidade sequenciais.
2. Se o cliente utilizou um e-mail temporário descartável (`tempmail.com`), o pedido é reprovado pelo filtro de fraude sem onerar o estoque.
3. Se os itens do carrinho não possuem saldo livre no armazém, o pedido é abortado antes do cálculo tributário.
4. Se todos os critérios forem atendidos, o filtro fiscal calcula o imposto de acordo com a unidade federativa de destino (`UF`) e consolida o valor final da cobrança.

---

## 💡 2. Justificativa Arquitetural

- **Por que Pipes and Filters aqui?**
  - **Padrão Short-Circuiting**: O `OrderValidationPipeline` interrompe a execução assim que qualquer filtro marca `is_approved = False`. Isso poupa chamadas de rede, consultas de estoque e requisições pagas a gateways de pagamento.
  - **Desacoplamento de Regras**: As regras fiscais de ICMS (`FiscalTaxFilter`) estão completamente isoladas da lógica de antifraude (`FraudRiskFilter`).
  - **Auditoria de Rejeição**: O pedido reprovado armazena exatamente qual estágio causou a recusa (`rejection_stage`) e a justificativa legível (`rejection_reason`).

---

## 📊 3. Diagrama do Pipeline com Short-Circuiting (Mermaid)

```mermaid
flowchart TD
    Source([Submissão do Pedido]) --> P0[Pipe]
    
    subgraph Pipeline ["Pipeline de Checkout de Pedidos"]
        P0 --> F1["SchemaValidationFilter<br/>(Campos & Valores)"]
        F1 --> C1{"Aprovado?"}
        C1 -- "Não" --> R1([Reprovado em SCHEMA])
        C1 -- "Sim" --> P1[Pipe]
        
        P1 --> F2["FraudRiskFilter<br/>(Antifraude & E-mails)"]
        F2 --> C2{"Aprovado?"}
        C2 -- "Não" --> R2([Reprovado em FRAUDE])
        C2 -- "Sim" --> P2[Pipe]
        
        P2 --> F3["InventoryCheckFilter<br/>(Disponibilidade de Estoque)"]
        F3 --> C3{"Aprovado?"}
        C3 -- "Não" --> R3([Reprovado em ESTOQUE])
        C3 -- "Sim" --> P3[Pipe]
        
        P3 --> F4["FiscalTaxFilter<br/>(ICMS por Estado Destino)"]
    end
    
    F4 --> Sink([Aprovado: Enviar ao Gateway])

    classDef pipe fill:#e2e8f0,stroke:#64748b,stroke-width:1px,color:#334155;
    classDef filter fill:#dbeafe,stroke:#2563eb,stroke-width:2px,color:#1e40af;
    classDef io fill:#fef3c7,stroke:#d97706,stroke-width:2px,color:#92400e;
    classDef rej fill:#fee2e2,stroke:#dc2626,stroke-width:1px,color:#991b1b;

    class P0,P1,P2,P3 pipe;
    class F1,F2,F3,F4 filter;
    class Source,Sink io;
    class R1,R2,R3 rej;
```

---

## 📁 4. Estrutura dos Arquivos

```text
05-ecommerce-order-checkout-pipeline/
├── README.md                           # Esta documentação
├── main.py                             # Execução com pedidos legítimos e reprovados
├── pipeline/
│   ├── base.py                         # Interface Filter e OrderValidationPipeline com short-circuit
│   └── context.py                      # OrderCheckoutContext e CheckoutItem
└── filters/
    ├── schema_validation_filter.py     # Checagem de integridade de dados e carrinho
    ├── fraud_risk_filter.py            # Avaliação de e-mails suspeitos e limites
    ├── inventory_check_filter.py       # Verificação de estoque físico
    └── fiscal_tax_filter.py            # Cálculo tributário interestadual (ICMS)
```

---

## 🧼 5. Princípios de Clean Code & SOLID Aplicados

- **Fail-Fast & Economia de Recursos**: Se a validação básica de schema falhar, o pipeline não executa consultas pesadas de estoque ou cálculos tributários.
- **Single Responsibility Principle (SRP)**: O `InventoryCheckFilter` recebe o inventário por injeção e se preocupa apenas com a quantidade livre de itens.
- **Encapsulamento de Propriedades**: Subtotais e totais finais são mantidos em atributos protegidos com arredondamento monetário preciso (`round(..., 2)`).

---

## ⚖️ 6. Trade-offs

| Vantagem | Custo / Limitação |
|---|---|
| Rejeição instantânea de pedidos fraudulentos sem onerar recursos internos | Se um pedido for reprovado no 3º estágio, nenhuma alteração prévia deve ter sido gravada de forma permanente (exige que as etapas prévias sejam apenas de leitura). |
| Fácil calibração de regras fiscais e antifraude | A esteira opera de forma estritamente serial; se os filtros fossem paralelos, demandaria um padrão *Scatter-Gather*. |

---

## 🚀 7. Como Executar

```bash
# A partir desta pasta:
python3 main.py
```
