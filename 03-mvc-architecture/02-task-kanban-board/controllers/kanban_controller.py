"""
kanban_controller.py - Camada de Controlador (Controller).

Interpreta ações do usuário no quadro (criar tarefa, mover card),
trata exceções de regras de negócio (como limite de WIP)
e comanda a re-renderização da View.
"""

from __future__ import annotations
from models.kanban_model import KanbanModel, TaskColumn, TaskPriority, WipLimitExceededException
from views.kanban_view import KanbanConsoleView


class KanbanController:
    def __init__(self, model: KanbanModel) -> None:
        self.model = model
        self.view = KanbanConsoleView()

    def create_task(self, title: str, priority: TaskPriority, assignee: str) -> str:
        task = self.model.add_task(title, priority, assignee)
        self.view.render_message(f"Tarefa '{task.task_id}' criada na coluna '{TaskColumn.TODO.value}'.")
        self.render_board()
        return task.task_id

    def move_task(self, task_id: str, target_column: TaskColumn) -> None:
        try:
            self.model.move_task(task_id, target_column)
            self.view.render_message(f"Tarefa '{task_id}' movida com sucesso para '{target_column.value}'.")
        except WipLimitExceededException as ex:
            self.view.render_message(f"⚠️ BLOQUEIO DE FLUXO: {ex}")
        except KeyError as ex:
            self.view.render_message(f"❌ ERRO: {ex}")
        finally:
            self.render_board()

    def render_board(self) -> None:
        columns_data = {
            TaskColumn.TODO: self.model.get_column_tasks(TaskColumn.TODO),
            TaskColumn.DOING: self.model.get_column_tasks(TaskColumn.DOING),
            TaskColumn.DONE: self.model.get_column_tasks(TaskColumn.DONE),
        }
        self.view.render(columns_data, self.model.doing_wip_limit)
