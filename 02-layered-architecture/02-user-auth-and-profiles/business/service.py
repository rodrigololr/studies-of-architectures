"""
service.py - Camada de Negócio (Business Layer).

Responsável por:
- Criptografia e salting seguro de senhas com PBKDF2.
- Registro com verificação de email duplicado.
- Autenticação e emissão de sessões.
- Verificação de controle de acesso por papel (RBAC).
"""

from __future__ import annotations
import hashlib
import os
import secrets
import uuid
from typing import Dict, Optional, Tuple
from business.exceptions import (
    UserAlreadyExistsException,
    InvalidCredentialsException,
    AccountDisabledException,
    UnauthorizedException,
)
from data.models import UserModel, UserRole
from data.repository import UserRepository


class AuthService:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository
        # Sessões em memória: token -> user_id
        self._sessions: Dict[str, str] = {}

    def _hash_password(self, password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        if not salt:
            salt = secrets.token_hex(16)
        pwd_bytes = password.encode("utf-8")
        salt_bytes = salt.encode("utf-8")
        key = hashlib.pbkdf2_hmac("sha256", pwd_bytes, salt_bytes, 100_000)
        return key.hex(), salt

    def register_user(
        self,
        full_name: str,
        email: str,
        raw_password: str,
        role: UserRole = UserRole.CUSTOMER,
    ) -> UserModel:
        if self.repository.find_by_email(email):
            raise UserAlreadyExistsException(f"Já existe uma conta cadastrada com o e-mail '{email}'.")

        if len(raw_password) < 6:
            raise InvalidCredentialsException("A senha deve possuir pelo menos 6 caracteres.")

        pwd_hash, salt = self._hash_password(raw_password)
        user = UserModel(
            user_id=str(uuid.uuid4())[:8],
            full_name=full_name.strip(),
            email=email.strip().lower(),
            password_hash=pwd_hash,
            salt=salt,
            role=role,
            is_active=True,
        )
        return self.repository.save(user)

    def login(self, email: str, raw_password: str) -> str:
        """Autentica o usuário e emite um token de sessão."""
        user = self.repository.find_by_email(email)
        if not user:
            raise InvalidCredentialsException("Credenciais inválidas.")

        if not user.is_active:
            raise AccountDisabledException("A conta está inativa.")

        expected_hash, _ = self._hash_password(raw_password, user.salt)
        if not secrets.compare_digest(expected_hash, user.password_hash):
            raise InvalidCredentialsException("Credenciais inválidas.")

        # Emite token seguro de sessão
        token = secrets.token_urlsafe(24)
        self._sessions[token] = user.user_id
        return token

    def authenticate_session(self, token: str, required_role: Optional[UserRole] = None) -> UserModel:
        """Valida o token e verifica se o usuário possui o papel necessário."""
        user_id = self._sessions.get(token)
        if not user_id:
            raise UnauthorizedException("Sessão inválida ou expirada.")

        user = self.repository.find_by_id(user_id)
        if not user or not user.is_active:
            raise UnauthorizedException("Usuário inexistente ou inativo.")

        if required_role and user.role != required_role:
            raise UnauthorizedException(
                f"Acesso negado: Perfil '{user.role.value}' não possui permissão de '{required_role.value}'."
            )

        return user
