"""
main.py - Demonstração executável do Sistema de Chamados em Camadas.

Demonstra ciclo de vida de tickets, cálculo de SLA para incidentes críticos,
transição de máquina de estados e bloqueio de transições inválidas.
"""

from data.repository import TicketRepository
from business.service import TicketService
from presentation.controller import TicketController


def main() -> None:
    print("=" * 65)
    print("DEMONSTRAÇÃO: Sistema de Tickets de Suporte e SLA em Camadas")
    print("=" * 65)

    repo = TicketRepository()
    service = TicketService(repo)
    controller = TicketController(service)

    # 1. Abertura de Ticket Crítico (SLA de 2 horas)
    print("\n[PASSO 1] POST /api/tickets (Abrindo Chamado Crítico)...")
    ticket_req = {
        "customer_id": "empresa-acme-corp",
        "title": "Indisponibilidade Total da API de Pagamentos em Produção",
        "description": "Gateway retornando erro 500 para todos os clientes.",
        "priority": "CRITICAL",
    }
    ticket_res = controller.open_ticket(ticket_req)
    print(f"  HTTP {ticket_res['status_code']}: {ticket_res['data']}")
    ticket_id = ticket_res["data"]["ticket_id"]

    # 2. Atribuição a um analista sênior (Move para IN_PROGRESS)
    print(f"\n[PASSO 2] POST /api/tickets/{ticket_id}/assign (Atribuindo a Engenheiro)...")
    assign_res = controller.assign(ticket_id, {"agent_id": "eng-marcos-sre"})
    print(f"  HTTP {assign_res['status_code']}: {assign_res['data']}")

    # 3. Tentativa inválida: Tentar fechar (CLOSE) direto sem resolver
    print(f"\n[PASSO 3] POST /api/tickets/{ticket_id}/close (Tentando fechar sem resolver)...")
    invalid_close = controller.close(ticket_id)
    print(f"  HTTP {invalid_close['status_code']} Unprocessable Entity: Erro = '{invalid_close['error']}'")

    # 4. Resolução correta do chamado (Move para RESOLVED)
    print(f"\n[PASSO 4] POST /api/tickets/{ticket_id}/resolve (Registrando resolução técnica)...")
    resolve_res = controller.resolve(
        ticket_id, {"notes": "Falha de conexão com o banco corrigida via failover de réplica."}
    )
    print(f"  HTTP {resolve_res['status_code']}: {resolve_res['data']}")

    # 5. Encerramento definitivo do chamado (Move para CLOSED)
    print(f"\n[PASSO 5] POST /api/tickets/{ticket_id}/close (Encerrando chamado formalmente)...")
    close_res = controller.close(ticket_id)
    print(f"  HTTP {close_res['status_code']}: {close_res['data']}")

    # 6. Tentativa de reabrir ou alterar chamado encerrado (Bloqueado)
    print(f"\n[PASSO 6] POST /api/tickets/{ticket_id}/assign (Tentando reatribuir chamado fechado)...")
    reassign_res = controller.assign(ticket_id, {"agent_id": "eng-outro"})
    print(f"  HTTP {reassign_res['status_code']} Unprocessable Entity: Erro = '{reassign_res['error']}'")

    print("\n" + "=" * 65)


if __name__ == "__main__":
    main()
