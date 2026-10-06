# Exemplo 01: Reserva e Emissão Aérea com GDS e ESB (Airline GDS Integration)

Este exemplo demonstra a aplicação da **Service-Oriented Architecture (SOA)** na integração entre canais modernos de venda (Web/Mobile REST/JSON) e sistemas legados de distribuição aérea (**GDS - Global Distribution Systems**, como Amadeus e Sabre), através de um **Enterprise Service Bus (ESB)** corporativo.

---

## 🎯 O Domínio do Problema

Na indústria da aviação civil:
1. **Sistemas Legados Heterogêneos:** Os inventários de assentos e voos residem em mainframes GDS que operam com comandos de texto plano (teletipo / EDIFACT).
2. **Canais Digitais:** Portais web e aplicativos mobile enviam solicitações em JSON/REST.
3. **Canonical Data Model (CDM):** O ESB atua como mediador traduzindo os payloads para um formato padronizado de reserva (`CanonicalReservationRequest` / `CanonicalReservationResponse`).
4. **Service Registry (Descobrabilidade):** O ESB descobre dinamicamente os endpoints e protocolos dos serviços registrados (`LegacyGdsService`, `CorporatePaymentService`, `ETicketIssuanceService`).
5. **Transação Compensatória no Barramento:** Se a cobrança do cartão for recusada após o assento ser reservado no GDS, o ESB cancela a reserva temporária (`CANCEL|PNR:...`) para não reter o inventário da aeronave.

---

## 🏛️ Diagrama de Arquitetura SOA (Mermaid)

```mermaid
sequenceDiagram
    autonumber
    actor Web as Canal Web / Mobile (REST/JSON)
    participant ESB as Enterprise Service Bus (ESB)
    participant Reg as Service Registry
    participant Trans as Message Transformer (CDM)
    participant GDS as Legacy GDS Service (TTY/EDIFACT)
    participant Pay as Corporate Payment Service (REST)
    participant Ticket as ETicket Issuance Service (IATA SOAP)

    Web->>ESB: POST /reservas (JSON)
    ESB->>Reg: lookup("LegacyGdsService", "CorporatePaymentService", ...)
    Reg-->>ESB: Metadados e Instâncias dos Serviços
    
    ESB->>Trans: web_json_to_canonical()
    Trans-->>ESB: CanonicalReservationRequest (CDM)
    
    ESB->>Trans: canonical_to_gds_tty()
    Trans-->>ESB: "HOLD|FLT:LA3301|PAX:SILVA/MARIA"
    ESB->>GDS: execute_terminal_command()
    GDS-->>ESB: "RESP:OK|PNR:78FB77|STATUS:HOLD"
    
    ESB->>Pay: authorize_and_charge(fare_amount)
    
    alt Pagamento Aprovado
        Pay-->>ESB: auth_code: "AUTH_1F280F4B"
        ESB->>Ticket: issue_eticket(pnr, passenger)
        Ticket-->>ESB: eticket_number: "957-5140089695"
        ESB-->>Web: 200 OK (PNR + E-Ticket Confirmado)
    else Pagamento Recusado (Compensação)
        Pay-->>ESB: Erro: Cartão Recusado
        ESB->>GDS: execute_terminal_command("CANCEL|PNR:78FB77")
        GDS-->>ESB: "RESP:OK|PNR:78FB77|STATUS:RELEASED"
        ESB-->>Web: 400 Bad Request (Reserva Cancelada)
    end
```

---

## 📁 Estrutura de Pastas

```
01-airline-booking-gds-integration/
├── canonical/
│   ├── __init__.py
│   └── flight_models.py
├── esb/
│   ├── __init__.py
│   ├── service_registry.py
│   ├── message_transformer.py
│   └── bus_orchestrator.py
├── services/
│   ├── __init__.py
│   ├── legacy_gds_service.py
│   ├── payment_service.py
│   └── eticket_service.py
├── main.py
└── README.md
```

---

## 🚀 Como Executar

Execute o comando a partir do diretório raiz:

```bash
python3 09-soa-service-oriented/01-airline-booking-gds-integration/main.py
```

### Cenários Validados no Teste:
1. **Emissão de Reserva com Sucesso:** Mapeamento de JSON Web para CDM, bloqueio de assento no GDS legado, liquidação financeira no gateway corporativo e emissão de bilhete IATA com prefixo 957.
2. **Compensação por Pagamento Recusado:** Quando o cartão é negado, o ESB comanda o cancelamento do PNR temporário no GDS legado para liberar o assento na aeronave.
3. **Governança e Falha no Registry:** O ESB recusa o processamento caso algum serviço corporativo essencial não esteja catalogado no `ServiceRegistry`.
