"""
main.py - Demonstração executável do Resolvedor de Nomes DNS (UDP + Cache).

Inicia o servidor de nomes UDP, realiza consultas no cliente,
demonstra o impacto de latência zero com o cache hit e a revalidação após TTL.
"""

import time
from server import DnsServer
from client import DnsClient


def main() -> None:
    print("=" * 65)
    print("DEMONSTRAÇÃO: Resolução de Nomes UDP com Cache e TTL")
    print("=" * 65)

    server = DnsServer(port=0)
    server.start()
    port = server.bound_port
    print(f"\n[SERVIDOR] DnsServer UDP ativo em 127.0.0.1:{port}")

    client = DnsClient(server_host="127.0.0.1", server_port=port)

    # 1. Primeira consulta: Deve ir para a rede (NETWORK_QUERY)
    domain_1 = "api.pagamentos.com"
    print(f"\n[1] Consultando '{domain_1}' pela primeira vez...")
    ip, source = client.resolve(domain_1)
    print(f"    Resultado: IP = {ip} | Origem = {source}")

    # 2. Segunda consulta imediata: Deve vir do cache (CACHE_HIT)
    print(f"\n[2] Consultando '{domain_1}' imediatamente em seguida...")
    ip, source = client.resolve(domain_1)
    print(f"    Resultado: IP = {ip} | Origem = {source}")

    # 3. Consulta de outro domínio
    domain_2 = "auth.empresa.com.br"
    print(f"\n[3] Consultando '{domain_2}'...")
    ip, source = client.resolve(domain_2)
    print(f"    Resultado: IP = {ip} | Origem = {source}")

    # 4. Domínio inexistente
    domain_unknown = "nao-existe.interno"
    print(f"\n[4] Consultando domínio inexistente '{domain_unknown}'...")
    ip, source = client.resolve(domain_unknown)
    print(f"    Resultado: IP = {ip} | Origem = {source}")

    # 5. Demonstração de expiração de TTL (configurado para 2 segundos no servidor)
    print(f"\n[5] Aguardando 2.2 segundos para expiração do TTL de '{domain_1}'...")
    time.sleep(2.2)
    print(f"    Consultando '{domain_1}' novamente após expiração...")
    ip, source = client.resolve(domain_1)
    print(f"    Resultado: IP = {ip} | Origem = {source} (Revalidado com sucesso no servidor!)")

    server.stop()
    print("\n[SERVIDOR] DnsServer finalizado.")
    print("=" * 65)


if __name__ == "__main__":
    main()
