"""
main.py - Demonstração executável do Mini-RPC Cliente-Servidor.

Registra procedimentos no servidor, efetua chamadas válidas,
demonstra erro de autenticação, método inexistente e divisão por zero remota.
"""

from server import RpcServer
from client import RpcClient, RemoteProcedureError


def main() -> None:
    print("=" * 65)
    print("DEMONSTRAÇÃO: Mini-RPC sobre TCP (JSON-RPC + Despachante)")
    print("=" * 65)

    secret_token = "auth-token-seguro-123"
    server = RpcServer(valid_token=secret_token, port=0)

    # 1. Registro de procedimentos de negócio no servidor
    def calcular_imposto(valor: float, aliquota_percentual: float) -> dict:
        imposto = valor * (aliquota_percentual / 100.0)
        return {"valor_base": valor, "imposto_devido": round(imposto, 2), "total": round(valor + imposto, 2)}

    def somar_numeros(a: float, b: float) -> float:
        return a + b

    def dividir_numeros(numerador: float, denominador: float) -> float:
        return numerador / denominador

    server.register_method("calcular_imposto", calcular_imposto)
    server.register_method("somar_numeros", somar_numeros)
    server.register_method("dividir_numeros", dividir_numeros)

    server.start()
    port = server.bound_port
    print(f"\n[SERVIDOR] RpcServer ativo na porta {port}")

    # 2. Cliente com credencial válida
    client = RpcClient(auth_token=secret_token, port=port)

    # Chamada 1: Cálculo de imposto
    print("\n[CHAMADA 1] Invocando 'calcular_imposto' remotamente...")
    resultado_imposto = client.call("calcular_imposto", valor=1500.0, aliquota_percentual=18.5)
    print(f"  Resultado retornado pelo servidor: {resultado_imposto}")

    # Chamada 2: Soma
    print("\n[CHAMADA 2] Invocando 'somar_numeros' remotamente...")
    resultado_soma = client.call("somar_numeros", a=42.5, b=57.5)
    print(f"  Resultado retornado: {resultado_soma}")

    # Chamada 3: Erro de execução remota (divisão por zero)
    print("\n[CHAMADA 3] Testando tratamento de exceção remota (divisão por zero)...")
    try:
        client.call("dividir_numeros", numerador=100.0, denominador=0.0)
    except RemoteProcedureError as err:
        print(f"  ✅ Exceção capturada com sucesso no cliente: {err}")

    # Chamada 4: Método inexistente
    print("\n[CHAMADA 4] Testando método não registrado...")
    try:
        client.call("procedimento_fantasma")
    except RemoteProcedureError as err:
        print(f"  ✅ Exceção capturada: {err}")

    # Chamada 5: Token inválido
    print("\n[CHAMADA 5] Testando cliente com token incorreto...")
    hacker_client = RpcClient(auth_token="token-falso", port=port)
    try:
        hacker_client.call("somar_numeros", a=1, b=1)
    except RemoteProcedureError as err:
        print(f"  ✅ Falha de autorização esperada: {err}")

    server.stop()
    print("\n[SERVIDOR] RpcServer encerrado.")
    print("=" * 65)


if __name__ == "__main__":
    main()
