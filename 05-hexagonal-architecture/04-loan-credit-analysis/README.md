# Exemplo 04: Loan Credit Analysis & Risk Underwriting

## 1. Visão Geral e Contexto de Negócio

A concessão de crédito em instituições bancárias e fintechs exige um motor de decisão altamente auditável, desacoplado e protegido contra variações de APIs externas. O motor deve receber dados do proponente (CPF, renda, valor pretendido, prazo), consultar múltiplos birôs de crédito (Serasa Experian, SPC Brasil, Quod), verificar o endividamento consolidado no BACEN SCR (Sistema de Informações de Crédito) e calcular a viabilidade financeira (comprometimento máximo de 30% da renda líquida).

A **Arquitetura Hexagonal** assegura que:
- O motor atuarial e as políticas regulatórias do BACEN permaneçam encapsulados no interior do hexágono.
- Novos birôs de proteção ao crédito possam ser plugados ou trocados sem alterar o cálculo de risco ou a tabela Price.
- A esteira possa ser disparada pelo aplicativo móvel de autoatendimento (via API REST) ou pelo sistema de caixa e gerência de agência física (via terminal console).

---

## 2. Diagrama da Arquitetura Hexagonal

```mermaid
flowchart LR
    subgraph Drivers ["Adaptadores Primários (Driver)"]
        API["LoanApplicationApiController\n(App Mobile / Web)"]
        TELLER["BankTellerConsoleAdapter\n(Terminal Agência Física)"]
    end

    subgraph Hexagon ["Hexágono: Motor de Crédito"]
        direction TB
        subgraph DriverPorts ["Portas de Entrada (Driver)"]
            UCP["UnderwriteCreditProposalUseCasePort\nevaluate(proposal)"]
            GDP["GetCreditDossierUseCasePort\nget_dossier(id)"]
        end

        subgraph CoreApp ["Aplicação & Domínio"]
            SVC["CreditUnderwritingService\n(Regras Regulatórias & Risco)"]
            DOM["Entidades & Regras:\nApplicant, LoanProposal\nCreditAnalysisResult, Rating AAA-B"]
        end

        subgraph DrivenPorts ["Portas de Saída (Driven)"]
            CBP["CreditBureauPort\nquery_score(cpf)"]
            SCR["CentralBankScrPort\nget_total_commitments(cpf)"]
            RPP["InterestRatePolicyPort\nget_annual_rate(rating)"]
            REP["CreditDossierRepositoryPort\nsave(result) / find_by_id(id)"]
        end
    end

    subgraph DrivenAdapters ["Adaptadores Secundários (Driven)"]
        direction TB
        SERASA["SerasaBureauAdapter\n(API Serasa Experian)"]
        SPC["SpcBureauAdapter\n(API SPC Brasil)"]
        BACEN["BacenScrAdapter\n(Consulta BACEN SCR)"]
        TAXA["BacenMarketRatePolicyAdapter\n(Tabela de Taxas)"]
        DB["InMemoryCreditDossierAdapter\n(Repositório de Dossiês)"]
    end

    API -->|chama| UCP
    TELLER -->|chama| UCP
    API -->|chama| GDP
    UCP --> SVC
    GDP --> SVC
    SVC --> DOM
    SVC -->|usa| CBP
    SVC -->|usa| SCR
    SVC -->|usa| RPP
    SVC -->|usa| REP
    CBP -.->|implementado por| SERASA
    CBP -.->|implementado por| SPC
    SCR -.->|implementado por| BACEN
    RPP -.->|implementado por| TAXA
    REP -.->|implementado por| DB
```

---

## 3. Estrutura do Exemplo

```text
04-loan-credit-analysis/
├── domain/
│   ├── models.py                     # Applicant, LoanProposal, CreditAnalysisResult, Rating
│   └── exceptions.py                 # InvalidProposalException, BureauUnavailableException
├── ports/
│   ├── driver.py                     # UnderwriteCreditProposalUseCasePort, GetCreditDossierUseCasePort
│   └── driven.py                     # CreditBureauPort, CentralBankScrPort, RatePolicy, Repository
├── core/
│   └── service.py                    # CreditUnderwritingService (Regras atuariais e amortização)
├── adapters/
│   ├── primary/
│   │   ├── loan_application_api_controller.py # Inbound REST API
│   │   └── bank_teller_console_adapter.py    # Inbound Terminal de Agência
│   └── secondary/
│       ├── serasa_bureau_adapter.py          # Outbound Serasa
│       ├── spc_bureau_adapter.py             # Outbound SPC
│       ├── bacen_scr_adapter.py              # Outbound Banco Central SCR
│       ├── market_rate_policy_adapter.py     # Outbound Política de Juros
│       └── in_memory_dossier_adapter.py      # Outbound Repositório
├── main.py                           # Composition Root e cenários de execução
└── README.md                         # Documentação técnica
```

---

## 4. Cenários Demonstrados no `main.py`

1. **Aprovação Rating AAA:** Proponente com renda sólida e score de 915 pontos; aprovação com taxa de juros competitiva e parcela dentro do limite.
2. **Reprovação por Restrição Cadastral:** Proponente com apontamento de inadimplência ativa; bloqueio preventivo antes do cálculo de parcelas.
3. **Reprovação por Capacidade de Pagamento:** Parcela excede a regra mandatória de 30% da renda líquida comprovada.
4. **Acionamento Multicanal:** Gerente de agência física operando no terminal de balcão utilizando o mesmo núcleo do aplicativo web.
5. **Rejeição por Regra de Domínio:** Bloqueio de propostas com renda negativa ou inconsistente.
6. **Recuperação de Dossiê:** Consulta do laudo detalhado gravado no repositório.

---

## 5. Como Executar

```bash
python3 main.py
```
