"""
kanban_view.py - Camada de Visão (View).

Desenha o quadro visual Kanban no terminal, com colunas alinhadas,
exibindo ID, título resumido, responsável e prioridade.
"""

from __future__ import annotations
from typing import Dict, List
from models.kanban_model import KanbanTask, TaskColumn


class KanbanConsoleView:
    @staticmethod
    def render(columns_data: Dict[TaskColumn, List[KanbanTask]], wip_limit: int) -> None:
        col_width = 30
        print("\n" + "=" * (col_width * 3 + 4))
        header_todo = f"📝 A FAZER ({len(columns_data[TaskColumn.TODO])})"
        header_doing = f"⚡ EM PROGRESSO ({len(columns_data[TaskColumn.DOING])}/{wip_limit})"
        header_done = f"✅ CONCLUÍDO ({len(columns_data[TaskColumn.DONE])})"

        print(f"| {header_todo:<{col_width-2}} | {header_doing:<{col_width-2}} | {header_done:<{col_width-2}} |")
        print("=" * (col_width * 3 + 4))

        todo_list = columns_data[TaskColumn.TODO]
        doing_list = columns_data[TaskColumn.DOING]
        done_list = columns_data[TaskColumn.DONE]

        max_rows = max(len(todo_list), len(doing_list), len(done_list), 1)

        for row_idx in range(max_rows):
            todo_txt = KanbanConsoleView._format_card(todo_list[row_idx], col_width - 2) if row_idx < len(todo_list) else ""
            doing_txt = KanbanConsoleView._format_card(doing_list[row_idx], col_width - 2) if row_idx < len(doing_list) else ""
            done_txt = KanbanConsoleView._format_card(done_list[row_idx], col_width - 2) if row_idx < len(done_list) else ""

            print(f"| {todo_txt:<{col_width-2}} | {doing_txt:<{col_width-2}} | {done_txt:<{col_width-2}} |")

        print("=" * (col_width * 3 + 4))

    @staticmethod
    def _format_card(task: KanbanTask, max_len: int) -> str:
        snippet = f"[{task.task_id}] {task.title}"
        if len(snippet) > max_len:
            snippet = snippet[:max_len - 3] + "..."
        return snippet

    @staticmethod
    def render_message(message: str) -> None:
        print(f"📢 [NOTIFICAÇÃO]: {message}")
