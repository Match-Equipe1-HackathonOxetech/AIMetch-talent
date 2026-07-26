from __future__ import annotations

from typing import Optional

from app.domain.entities import Entrevista, PerguntaTemplate, Resultado, Vaga
from app.domain.value_objects import Memoria, ResultadoIA, ResumoIA, SoftskillEstado, StatusSoftskill
from app.ports.llm_port import LLMPort
from app.ports.repositories import (
    EntrevistaRepository,
    PerguntaTemplateRepository,
    ResultadoRepository,
    VagaRepository,
)


class FakeVagaRepository(VagaRepository):
    def __init__(self):
        self._vagas: dict[str, Vaga] = {}

    def salvar(self, vaga: Vaga) -> None:
        self._vagas[vaga.id] = vaga

    def buscar(self, vaga_id: str) -> Optional[Vaga]:
        return self._vagas.get(vaga_id)


class FakePerguntaTemplateRepository(PerguntaTemplateRepository):
    def buscar_por_softskill(self, softskill: Optional[str]) -> Optional[PerguntaTemplate]:
        if softskill is None:
            return None
        return PerguntaTemplate(softskill=softskill, texto=f"Fale sobre uma situação de {softskill}.")


class FakeEntrevistaRepository(EntrevistaRepository):
    def __init__(self):
        self._entrevistas: dict[str, Entrevista] = {}

    def salvar(self, entrevista: Entrevista) -> None:
        self._entrevistas[entrevista.id] = entrevista

    def buscar(self, entrevista_id: str) -> Optional[Entrevista]:
        return self._entrevistas.get(entrevista_id)


class FakeResultadoRepository(ResultadoRepository):
    def __init__(self):
        self._resultados: dict[str, Resultado] = {}

    def salvar(self, resultado: Resultado) -> None:
        self._resultados[resultado.entrevista_id] = resultado

    def buscar_por_entrevista(self, entrevista_id: str) -> Optional[Resultado]:
        return self._resultados.get(entrevista_id)

    def listar_por_vaga(self, vaga_id: str) -> list[Resultado]:
        return list(self._resultados.values())


class FakeLLMPort(LLMPort):
    """
    Devolve respostas fixas e determinísticas: avança uma softskill por
    chamada e conclui quando todas estiverem avaliadas. Não faz nenhuma
    chamada de rede — é isso que permite testar EntrevistaService sem
    depender do Gemini de verdade.
    """

    def gerar_pergunta(self, vaga, memoria: Memoria, pergunta_template, resposta) -> ResultadoIA:
        nova_memoria = Memoria(
            softskills=[SoftskillEstado(**s.__dict__) for s in memoria.softskills],
            contexto_pessoal=dict(memoria.contexto_pessoal),
            ganchos_usados=list(memoria.ganchos_usados),
        )

        softskill_atual = nova_memoria.softskill_atual()
        if softskill_atual is not None and resposta is not None:
            for s in nova_memoria.softskills:
                if s.nome == softskill_atual:
                    s.status = StatusSoftskill.AVALIADA
                    s.pontuacao = 8.0

        concluida = nova_memoria.todas_avaliadas()
        proxima = None if concluida else f"Pergunta fixa para {nova_memoria.softskill_atual()}"
        return ResultadoIA(proxima_pergunta=proxima, memoria_atualizada=nova_memoria, concluida=concluida)

    def gerar_resumo_resultado(self, vaga, memoria: Memoria) -> ResumoIA:
        return ResumoIA(resumo="Resumo fixo de teste", recomendacao="Recomendado")
