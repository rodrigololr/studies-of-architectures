"""
controller.py - Camada de Apresentação (Presentation Layer).

Recebe requisições de cadastro, login e rotas protegidas administrativas,
nunca expondo o salt ou hash da senha na resposta do cliente.
"""

from __future__ import annotations
from typing import Any, Dict
from business.service import AuthService
from business.exceptions import BusinessException, UnauthorizedException, InvalidCredentialsException
from data.models import UserRole


class AuthController:
    def __init__(self, service: AuthService) -> None:
        self.service = service

    def register(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """POST /api/auth/register"""
        try:
            role_str = payload.get("role", "CUSTOMER")
            role = UserRole(role_str)
            user = self.service.register_user(
                full_name=payload.get("full_name", ""),
                email=payload.get("email", ""),
                raw_password=payload.get("password", ""),
                role=role,
            )
            # Response DTO: Jamais expõe password_hash ou salt!
            return {
                "status_code": 201,
                "data": {
                    "user_id": user.user_id,
                    "full_name": user.full_name,
                    "email": user.email,
                    "role": user.role.value,
                },
            }
        except BusinessException as ex:
            return {"status_code": 400, "error": str(ex)}

    def login(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """POST /api/auth/login"""
        try:
            token = self.service.login(
                email=payload.get("email", ""),
                raw_password=payload.get("password", ""),
            )
            return {"status_code": 200, "data": {"token": token, "token_type": "Bearer"}}
        except InvalidCredentialsException as ex:
            return {"status_code": 401, "error": str(ex)}
        except BusinessException as ex:
            return {"status_code": 400, "error": str(ex)}

    def get_admin_dashboard(self, auth_header: str) -> Dict[str, Any]:
        """GET /api/admin/dashboard (Rota protegida para ADMIN)"""
        try:
            token = auth_header.replace("Bearer ", "").strip()
            user = self.service.authenticate_session(token, required_role=UserRole.ADMIN)
            return {
                "status_code": 200,
                "data": {
                    "message": f"Bem-vindo ao painel confidencial, Administrador {user.full_name}!",
                    "server_health": "100% Operacional",
                },
            }
        except UnauthorizedException as ex:
            return {"status_code": 403, "error": str(ex)}
