"""
Portas de persistência.

Cada porta é uma interface mínima (buscar/salvar/listar) que o domínio usa sem
saber se por trás existe SQLAlchemy, um banco em memória (testes) ou qualquer
outra coisa. Os adapters concretos estão em
app/adapters/outbound/persistence/sql_repositories.py.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from app.domain.entities import (
    Candidato,
    Empresa,
    Entrevista,
    PerguntaTemplate,
    RefreshToken,
    Resultado,
    Vaga,
)


class EmpresaRepository(ABC):
    @abstractmethod
    def salvar(self, empresa: Empresa) -> None: ...

    @abstractmethod
    def buscar(self, empresa_id: str) -> Optional[Empresa]: ...

    @abstractmethod
    def buscar_por_email(self, email: str) -> Optional[Empresa]: ...


class CandidatoRepository(ABC):
    @abstractmethod
    def salvar(self, candidato: Candidato) -> None: ...

    @abstractmethod
    def buscar(self, candidato_id: str) -> Optional[Candidato]: ...

    @abstractmethod
    def buscar_por_email(self, email: str) -> Optional[Candidato]: ...


class VagaRepository(ABC):
    @abstractmethod
    def salvar(self, vaga: Vaga) -> None: ...

    @abstractmethod
    def buscar(self, vaga_id: str) -> Optional[Vaga]: ...


class PerguntaTemplateRepository(ABC):
    @abstractmethod
    def buscar_por_softskill(self, softskill: str) -> Optional[PerguntaTemplate]: ...


class EntrevistaRepository(ABC):
    @abstractmethod
    def salvar(self, entrevista: Entrevista) -> None: ...

    @abstractmethod
    def buscar(self, entrevista_id: str) -> Optional[Entrevista]: ...


class ResultadoRepository(ABC):
    @abstractmethod
    def salvar(self, resultado: Resultado) -> None: ...

    @abstractmethod
    def buscar_por_entrevista(self, entrevista_id: str) -> Optional[Resultado]: ...

    @abstractmethod
    def listar_por_vaga(self, vaga_id: str) -> list[Resultado]: ...


class RefreshTokenRepository(ABC):
    @abstractmethod
    def salvar(self, refresh_token: RefreshToken) -> None: ...

    @abstractmethod
    def buscar_por_token(self, token: str) -> Optional[RefreshToken]: ...

    @abstractmethod
    def revogar(self, token: str) -> None: ...

class VagaRepository(ABC):
    @abstractmethod
    def salvar(self, vaga: Vaga) -> None: ...

    @abstractmethod
    def buscar(self, vaga_id: str) -> Optional[Vaga]: ...

    @abstractmethod
    def listar_por_empresa(self, empresa_id: str) -> list[Vaga]: ...
