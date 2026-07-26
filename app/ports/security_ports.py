from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


class PasswordHasherPort(ABC):
    @abstractmethod
    def gerar_hash(self, senha_texto: str) -> str: ...

    @abstractmethod
    def verificar(self, senha_texto: str, senha_hash: str) -> bool: ...


@dataclass
class ParDeTokens:
    access_token: str
    refresh_token: str


class TokenServicePort(ABC):
    """
    Emite e decodifica JWTs de access/refresh. `role` é sempre "recrutado"
    (candidato) ou "recrutador" (empresa) e vai no payload do access_token
    para os endpoints checarem permissão.
    """

    @abstractmethod
    def emitir_par(self, usuario_id: str, role: str) -> ParDeTokens: ...

    @abstractmethod
    def decodificar_access_token(self, token: str) -> dict: ...

    @abstractmethod
    def decodificar_refresh_token(self, token: str) -> dict: ...
