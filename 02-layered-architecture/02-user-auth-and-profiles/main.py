"""
main.py - Demonstração executável de Autenticação e Perfis (Arquitetura em Camadas).

Demonstra cadastro, login seguro, emissão de tokens, restrição por perfil (RBAC)
e tratamento de erros de credenciais.
"""

from data.repository import UserRepository
from business.service import AuthService
from presentation.controller import AuthController


def main() -> None:
    print("=" * 65)
    print("DEMONSTRAÇÃO: Autenticação, Perfis e RBAC em Camadas")
    print("=" * 65)

    # 1. Montagem das camadas
    repo = UserRepository()
    service = AuthService(repo)
    controller = AuthController(service)

    # 2. Cadastro de Administrador
    print("\n[CADASTRO 1] Registrando Administrador...")
    admin_req = {
        "full_name": "Carlos Silva",
        "email": "carlos.admin@empresa.com",
        "password": "SenhaUltraSegura123!",
        "role": "ADMIN",
    }
    admin_res = controller.register(admin_req)
    print(f"  HTTP {admin_res['status_code']}: {admin_res['data']}")

    # 3. Cadastro de Cliente comum
    print("\n[CADASTRO 2] Registrando Usuário Cliente...")
    user_req = {
        "full_name": "Beatriz Lima",
        "email": "beatriz@cliente.com",
        "password": "MinhaSenha456!",
        "role": "CUSTOMER",
    }
    user_res = controller.register(user_req)
    print(f"  HTTP {user_res['status_code']}: {user_res['data']}")

    # 4. Tentativa de cadastro duplicado com mesmo email
    print("\n[CADASTRO 3] Tentativa de duplicidade de e-mail...")
    dup_res = controller.register(user_req)
    print(f"  HTTP {dup_res['status_code']}: Erro = '{dup_res['error']}'")

    # 5. Login com sucesso do Admin
    print("\n[LOGIN] Autenticando Administrador...")
    login_req = {"email": "carlos.admin@empresa.com", "password": "SenhaUltraSegura123!"}
    login_admin = controller.login(login_req)
    admin_token = login_admin["data"]["token"]
    print(f"  HTTP {login_admin['status_code']}: Token gerado = '{admin_token[:12]}...'")

    # 6. Login do Cliente
    login_client = controller.login({"email": "beatriz@cliente.com", "password": "MinhaSenha456!"})
    client_token = login_client["data"]["token"]

    # 7. Acesso à rota protegida administrativa pelo Admin (Permitido)
    print("\n[AUTORIZAÇÃO 1] Admin acessando painel restrito...")
    dash_admin = controller.get_admin_dashboard(f"Bearer {admin_token}")
    print(f"  HTTP {dash_admin['status_code']}: {dash_admin['data']['message']}")

    # 8. Tentativa de acesso à rota protegida pelo Cliente comum (Bloqueado via RBAC)
    print("\n[AUTORIZAÇÃO 2] Cliente tentando acessar painel restrito de Admin...")
    dash_client = controller.get_admin_dashboard(f"Bearer {client_token}")
    print(f"  HTTP {dash_client['status_code']}: Bloqueio 403 = '{dash_client['error']}'")

    print("\n" + "=" * 65)


if __name__ == "__main__":
    main()
