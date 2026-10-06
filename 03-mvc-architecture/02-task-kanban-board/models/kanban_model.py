"""
kanban_model.py - Camada de Modelo (Model).

Gerencia as tarefas, colunas do quadro Kanban e limites de WIP (Work in Progress).
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional
import uuid


class TaskPriority(str, Enum):
    LOW = "BAIXA"
    MEDIUM = "MÉDIA"
    HIGH = "ALTA"


class TaskColumn(str, Enum):
    TODO = "A FAZER"
    DOING = "EM PROGRESSO"
    DONE = "CONCLUÍDO"


@dataclass
class KanbanTask:
    task_id: str
    title: str
    priority: TaskPriority
    assignee: str
    column: TaskColumn = TaskColumn.TODO


class WipLimitExceededException(Exception):
    """Lançada quando a coluna excede o limite máximo de trabalho em progresso."""
    pass


class KanbanModel:
    def __init__(self, doing_wip_limit: int = 3) -> None:
        self.doing_wip_limit = doing_wip_limit
        self._tasks: Dict[str, KanbanTask] = {}

    def add_task(self, title: str, priority: TaskPriority, assignee: str) -> KanbanTask:
        task = KanbanTask(
            task_id=f"T-{str(uuid.uuid4())[:4].upper()}",
            title=title.strip(),
            priority=priority,
            assignee=assignee.strip(),
            column=TaskColumn.TODO,
        )
        self._tasks[task.task_id] = task
        return task

    def move_task(self, task_id: str, target_column: TaskColumn) -> KanbanTask:
        task = self._tasks.get(task_id)
        if not task:
            raise KeyError(f"Tarefa '{task_id}' não encontrada no quadro.")

        # Regra de Limite de WIP em DOING
        if target_column == TaskColumn.DOING:
            current_doing = sum(1 for t in self._tasks.values() if t.column == TaskColumn.DOING and t.task_id != task_id)
            if current_doing >= self.doing_wip_limit:
                raise WipLimitExceededException(
                    f"Limite de WIP atingido: máx. de {self.doing_wip_limit} tarefas permitidas em '{TaskColumn.DOING.value}'."
                )

        task.column = target_column
        return task

    def get_column_tasks(self, column: TaskColumn) -> List[KanbanTask]:
        return [t for t in self._tasks.values() if t.column == column]
