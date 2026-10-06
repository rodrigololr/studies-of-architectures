# Exemplo 06: B2B CRM Lead Enrichment & Scoring Pipeline

## 1. Visão Geral e Contexto de Negócio

Em estratégias de vendas B2B (Salesforce, HubSpot, Apollo), a qualificação rápida e precisa de novos contatos (*inbound leads*) determina a taxa de conversão comercial. O pipeline deve executar:
- **Validação de Domínio Corporativo:** Rejeição de endereços gratuitos (@gmail, @hotmail) para evitar ruído no funil de vendas.
- **Enriquecimento Firmográfico:** Consulta a fontes de inteligência de mercado para descobrir porte de funcionários e faturamento estimado da empresa.
- **Pontuação Ponderada na Entidade (Lead Scoring):** A entidade `Lead` calcula a pontuação somando critérios de tamanho, receita e senioridade do contato (C-Level, Diretor, Gerente).
- **Atribuição Automatizada (SDR/Account Executive):** Encaminhamento do lead para vendedores especializados conforme o porte (Enterprise, Mid-Market ou SMB).

A **Clean Architecture** permite que a fórmula de scoring e os critérios de roteamento comercial sejam alterados e testados com rapidez, sem acoplamento a APIs específicas de CRM ou serviços de terceiros de dados firmográficos.

---

## 2. Diagrama das Camadas da Clean Architecture

```mermaid
flowchart TD
    subgraph L4 ["🔵 Frameworks & Drivers"]
        MAIN["main.py (Composition Root)"]
    end

    subgraph L3 ["🟢 Interface Adapters"]
        CTRL["LeadIngestionController\n(handle_post_lead)"]
        PRES["LeadQualificationPresenter\n(Formata JSON QUALIFIED / DISQUALIFIED)"]
        REPO_LEAD["InMemoryLeadRepository"]
        GW_FIRMO["MockFirmographicGateway\n(Clearbit / ZoomInfo)"]
        REPO_REP["InMemorySalesRepRepository"]
    end

    subgraph L2 ["🔴 Use Cases"]
        IN_BOUND["IngestLeadInputBoundary\nexecute(request)"]
        INTERACTOR["IngestLeadInteractor\n(Orquestração e Atribuição de Vendedor)"]
        OUT_BOUND["IngestLeadOutputBoundary\npresent(response)"]
        GATEWAYS["LeadRepositoryGateway\nFirmographicEnrichmentGateway\nSalesRepRepositoryGateway"]
        DTOS["IngestLeadRequestModel\nIngestLeadResponseModel"]
    end

    subgraph L1 ["🟡 Entities"]
        LEAD["Lead\ncalculate_qualification_score()\nvalidate_corporate_domain()"]
        REP["SalesRep (RepTier)"]
    end

    MAIN --> CTRL
    MAIN --> PRES
    MAIN --> REPO_LEAD
    MAIN --> GW_FIRMO
    MAIN --> REPO_REP

    CTRL --> IN_BOUND
    IN_BOUND --> INTERACTOR
    INTERACTOR --> LEAD
    INTERACTOR --> REP
    INTERACTOR --> OUT_BOUND
    INTERACTOR --> GATEWAYS
    INTERACTOR -.-> DTOS

    PRES -.->|implementa| OUT_BOUND
    REPO_LEAD -.->|implementa| GATEWAYS
    GW_FIRMO -.->|implementa| GATEWAYS
    REPO_REP -.->|implementa| GATEWAYS
```

---

## 3. Estrutura do Exemplo

```text
06-crm-lead-enrichment-pipeline/
├── entities/
│   ├── models.py                     # Lead, SalesRep, calculate_qualification_score
│   └── exceptions.py                 # CrmEntityException
├── use_cases/
│   ├── dto.py                        # IngestLeadRequestModel, ResponseModel
│   ├── boundaries.py                 # InputBoundary, OutputBoundary, Gateways
│   └── interactors.py                # IngestLeadInteractor
├── interface_adapters/
│   ├── controllers.py                # LeadIngestionController
│   ├── presenters.py                 # LeadQualificationPresenter
│   └── gateways.py                   # Repositórios e Gateway firmográfico
├── main.py                           # Composition Root e cenários de execução
└── README.md                         # Documentação técnica
```

---

## 4. Cenários Demonstrados no `main.py`

1. **Lead Enterprise (HOT):** CTO de empresa com 1.200 colaboradores e US$ 85M de receita; atinge 100 pontos e é roteado para o executivo de contas Enterprise.
2. **Lead Mid-Market (WARM):** Gerente de TI em empresa de médio porte; atinge 65 pontos e é atribuído ao time Mid-Market.
3. **Lead SMB (COLD):** Atendente de microempresa; atinge 15 pontos e é direcionado para nutrição por automação (SMB).
4. **Desqualificação Preventiva:** Rejeição imediata de cadastro com e-mail gratuito pessoal (@gmail.com).

---

## 5. Como Executar

```bash
python3 main.py
```
