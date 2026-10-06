"""
main.py - Demonstração executável do Quadro Kanban em MVC.

Simula adição de tarefas, movimentações de cartões entre colunas,
tentativa de violação do limite de WIP (Work-In-Progress) e conclusão de cards.
"""

from models.kanban_model import KanbanModel, TaskColumn, TaskPriority
from controllers.kanban_controller import KanbanController


def main() -> None:
    print("=" * 70)
    print("DEMONSTRAÇÃO: Arquitetura MVC (Quadro Kanban com Limite de WIP)")
    print("=" * 70)

    # 1. Configura o Model com limite máximo de 2 tarefas em DOING
    model = KanbanModel(doing_wip_limit=2)
    controller = KanbanController(model)

    # 2. Usuário cria tarefas
    t1 = controller.create_task("Configurar Banco PostgreSQL", TaskPriority.HIGH, "Dev Alice")
    t2 = controller.create_task("Implementar Login JWT", TaskPriority.HIGH, "Dev Bob")
    t3 = controller.create_task("Criar Testes de Carga", TaskPriority.MEDIUM, "Dev Carlos")
    t4 = controller.create_task("Documentar Endpoints OpenAPI", TaskPriority.LOW, "Dev Diana")

    # 3. Usuário move tarefas para EM PROGRESSO
    print("\n--- Movendo 2 Tarefas para EM PROGRESSO (Atingindo Limite de 2) ---")
    controller.move_task(t1, TaskColumn.DOING)
    controller.move_task(t2, TaskColumn.DOING)

    # 4. Tentativa de mover uma 3ª tarefa para DOING (Violação de WIP)
    print("\n--- Tentando mover uma 3ª tarefa para EM PROGRESSO (Bloqueio Esperado) ---")
    controller.move_task(t3, TaskColumn.DOING)

    # 5. Concluindo uma tarefa e liberando vaga no WIP
    print("\n--- Concluindo uma tarefa (Liberando espaço no fluxo de trabalho) ---")
    controller.move_task(t1, TaskColumn.DONE)

    # 6. Agora a 3ª tarefa pode ser puxada para DOING com sucesso!
    print("\n--- Puxando a 3ª tarefa agora que há espaço no limite de WIP ---")
    controller.move_task(t3, TaskColumn.DOING)


if __name__ == "__main__":
    main()
