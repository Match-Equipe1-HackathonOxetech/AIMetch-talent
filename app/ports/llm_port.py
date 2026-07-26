"""
LLMPort é a única porta pela qual o domínio "conversa" com uma IA.

EntrevistaService conhece apenas esta interface. Ela não sabe que por trás
existe Gemini, outro provedor, ou um fake de teste — só que, dado o estado
atual da entrevista, recebe de volta uma pergunta, uma memória atualizada e
um resumo final quando pedido.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from app.domain.entities import PerguntaTemplate, Vaga
from app.domain.value_objects import Memoria, ResultadoIA, ResumoIA


class LLMPort(ABC):

    @abstractmethod
    def gerar_pergunta(
        self,
        vaga: Vaga,
        memoria: Memoria,
        pergunta_template: Optional[PerguntaTemplate],
        resposta: Optional[str],
    ) -> ResultadoIA:
        """
        Gera o próximo turno da entrevista.

        `resposta` é None apenas na primeira chamada (abertura da entrevista);
        em todas as demais é a resposta em texto livre do candidato ao turno
        anterior. `pergunta_template` é o modelo de pergunta cadastrado para a
        softskill em foco (`memoria.softskill_atual()`), usado como ponto de
        partida — a IA pode adaptar o texto, mas deve continuar avaliando a
        mesma softskill.
        """
        ...

    @abstractmethod
    def gerar_resumo_resultado(self, vaga: Vaga, memoria: Memoria) -> ResumoIA:
        """Consolida a memória final (já com todas as softskills avaliadas) em um resumo e recomendação."""
        ...
