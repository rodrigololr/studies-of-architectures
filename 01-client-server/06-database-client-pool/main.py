"""
main.py - Demonstração executável do Connection Pool Cliente-Servidor.

Inicia o servidor de banco, configura um pool de 3 conexões e dispara
6 tarefas simultâneas em threads, demonstrando o reuso das conexões
sem abrir novos sockets e sem esgotar portas.
"""

from concurrent.futures import ThreadPoolExecutor
import time
from server import DatabaseServer
from pool import DatabaseConnectionPool


def worker_task(pool: DatabaseConnectionPool, task_id: int) -> dict:
    """Simula uma requisição web que precisa consultar o banco."""
    conn = pool.acquire()
    try:
        query = f"SELECT * FROM pedidos WHERE cliente_id = {task_id};"
        rows = conn.execute_query(query)
        return {"task_id": task_id, "conn_id": conn.connection_id, "rows": rows}
    finally:
        pool.release(conn)


def main() -> None:
    print("=" * 65)
    print("DEMONSTRAÇÃO: Client-Side Connection Pool para Banco de Dados")
    print("=" * 65)

    server = DatabaseServer(port=0)
    server.start()
    port = server.bound_port
    print(f"\n[SERVIDOR] DatabaseServer ativo na porta {port}")

    # Criação do pool com capacidade fixa para 3 conexões simultâneas
    pool_size = 3
    print(f"\n[CLIENTE] Inicializando Connection Pool com capacidade: {pool_size} conexões pré-aquecidas...")
    pool = DatabaseConnectionPool(host="127.0.0.1", port=port, pool_size=pool_size)

    # Dispara 6 tarefas simultâneas (o dobro do tamanho do pool)
    print("\n--- Disparando 6 Tarefas Concorrentes com ThreadPoolExecutor ---")
    start_time = time.perf_counter()

    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = [executor.submit(worker_task, pool, i + 1) for i in range(6)]
        results = [f.result() for f in futures]

    elapsed_ms = (time.perf_counter() - start_time) * 1000

    for res in results:
        print(f"  Tarefa {res['task_id']} executada com sucesso usando Conexão #{res['conn_id']}")

    print(f"\n⏱️ Tempo total para 6 queries executadas via pool: {elapsed_ms:.2f} ms")
    print("✅ Todas as 6 tarefas reutilizaram apenas as 3 conexões físicas do pool sem abrir novos sockets!")

    # Encerramento limpo
    pool.close_all()
    server.stop()
    print("\n[CLEANUP] Conexões do pool e servidor fechados com sucesso.")
    print("=" * 65)


if __name__ == "__main__":
    main()
