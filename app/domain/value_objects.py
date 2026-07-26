"""
Value objects do domínio da entrevista.

`Memoria` é o estado conversacional que atravessa toda a entrevista: quais
softskills já foram avaliadas, com que pontuação, o contexto pessoal coletado
ao longo da conversa e quais "ganchos" (referências a algo que o candidato já
disse) já foram usados pela IA para não repetir abordagem.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class StatusSoftskill(str, Enum):
    PENDENTE = "pendente"
    EM_AVALIACAO = "em_avaliacao"
    AVALIADA = "avaliada"


@dataclass
class SoftskillEstado:
    nome: str
    status: StatusSoftskill = StatusSoftskill.PENDENTE
    pontuacao: Optional[float] = None

    def to_dict(self) -> dict:
        return {"nome": self.nome, "status": self.status.value, "pontuacao": self.pontuacao}

    @staticmethod
    def from_dict(data: dict) -> "SoftskillEstado":
        return SoftskillEstado(
            nome=data["nome"],
            status=StatusSoftskill(data.get("status", "pendente")),
            pontuacao=data.get("pontuacao"),
        )


@dataclass
class Memoria:
    softskills: list[SoftskillEstado]
    contexto_pessoal: dict[str, Any] = field(default_factory=dict)
    ganchos_usados: list[str] = field(default_factory=list)

    @staticmethod
    def vazia(softskills_alvo: list[str]) -> "Memoria":
        return Memoria(softskills=[SoftskillEstado(nome=s) for s in softskills_alvo])

    def softskill_atual(self) -> Optional[str]:
        """Primeira softskill ainda não avaliada — é nela que o próximo turno foca."""
        for s in self.softskills:
            if s.status != StatusSoftskill.AVALIADA:
                return s.nome
        return None

    def todas_avaliadas(self) -> bool:
        return all(s.status == StatusSoftskill.AVALIADA for s in self.softskills)

    def to_dict(self) -> dict:
        return {
            "softskills": [s.to_dict() for s in self.softskills],
            "contexto_pessoal": self.contexto_pessoal,
            "ganchos_usados": self.ganchos_usados,
        }

    @staticmethod
    def from_dict(data: dict) -> "Memoria":
        return Memoria(
            softskills=[SoftskillEstado.from_dict(s) for s in data.get("softskills", [])],
            contexto_pessoal=data.get("contexto_pessoal", {}),
            ganchos_usados=data.get("ganchos_usados", []),
        )


@dataclass
class ResultadoIA:
    """Retorno de um turno de entrevista (LLMPort.gerar_pergunta)."""
    proxima_pergunta: Optional[str]
    memoria_atualizada: Memoria
    concluida: bool


@dataclass
class ResumoIA:
    """Retorno da consolidação final (LLMPort.gerar_resumo_resultado)."""
    resumo: str
    recomendacao: str
