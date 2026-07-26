"""
Entidades de domínio.

Nenhuma classe aqui conhece Flask, SQLAlchemy ou Gemini — são apenas dados e
comportamento de negócio puro. A conversão para/de linhas de banco acontece nos
adapters de persistência (app/adapters/outbound/persistence).
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from app.domain.value_objects import Memoria


def novo_id() -> str:
    return uuid.uuid4().hex


@dataclass
class Empresa:
    nome: str
    email: str
    senha_hash: str
    id: str = field(default_factory=novo_id)


@dataclass
class Candidato:
    nome: str
    email: str
    senha_hash: str
    id: str = field(default_factory=novo_id)


@dataclass
class Vaga:
    empresa_id: str
    titulo: str
    softskills_alvo: list[str]
    id: str = field(default_factory=novo_id)


@dataclass
class PerguntaTemplate:
    softskill: str
    texto: str
    id: str = field(default_factory=novo_id)


@dataclass
class Entrevista:
    candidato_id: str
    vaga_id: str
    memoria: Memoria
    status: str = "em_andamento"  # "em_andamento" | "concluida"
    id: str = field(default_factory=novo_id)
    criada_em: datetime = field(default_factory=datetime.utcnow)

    def concluir(self) -> None:
        self.status = "concluida"

    @property
    def concluida(self) -> bool:
        return self.status == "concluida"


@dataclass
class Resultado:
    entrevista_id: str
    pontuacoes: dict[str, float]
    resumo: str
    recomendacao: str
    id: str = field(default_factory=novo_id)


@dataclass
class RefreshToken:
    """Registro de um refresh_token emitido, para permitir invalidação (logout)."""
    usuario_id: str
    role: str
    token: str
    expira_em: datetime
    revogado: bool = False
    id: str = field(default_factory=novo_id)
