from __future__ import annotations

from typing import Optional

from app.domain.entities import Entrevista, Resultado
from app.domain.exceptions import AcessoNegado, EntrevistaJaConcluida, RecursoNaoEncontrado
from app.domain.value_objects import Memoria
from app.ports.llm_port import LLMPort
from app.ports.repositories import (
    EntrevistaRepository,
    PerguntaTemplateRepository,
    ResultadoRepository,
    VagaRepository,
)


class EntrevistaService:
    """
    Caso de uso da entrevista conversacional. Esta classe é o "canal-agnóstico"
    citado no requisito: um handler de bot do Telegram ou WhatsApp chamaria
    exatamente estes mesmos métodos, sem duplicar nenhuma regra — a única
    coisa que muda por canal é o adapter de entrada (rota HTTP, webhook do
    bot, etc.), nunca a lógica aqui dentro.
    """

    def __init__(
        self,
        entrevista_repo: EntrevistaRepository,
        vaga_repo: VagaRepository,
        pergunta_repo: PerguntaTemplateRepository,
        resultado_repo: ResultadoRepository,
        llm: LLMPort,
    ):
        self.entrevista_repo = entrevista_repo
        self.vaga_repo = vaga_repo
        self.pergunta_repo = pergunta_repo
        self.resultado_repo = resultado_repo
        self.llm = llm

    def iniciar_entrevista(self, candidato_id: str, vaga_id: str) -> tuple[str, Optional[str]]:
        vaga = self.vaga_repo.buscar(vaga_id)
        if vaga is None:
            raise RecursoNaoEncontrado("Vaga não encontrada")

        memoria = Memoria.vazia(softskills_alvo=vaga.softskills_alvo)
        pergunta_template = self.pergunta_repo.buscar_por_softskill(memoria.softskill_atual())
        resultado = self.llm.gerar_pergunta(vaga, memoria, pergunta_template, resposta=None)

        entrevista = Entrevista(candidato_id=candidato_id, vaga_id=vaga_id, memoria=resultado.memoria_atualizada)
        if resultado.concluida:
            entrevista.concluir()
        self.entrevista_repo.salvar(entrevista)

        return entrevista.id, resultado.proxima_pergunta

    def responder(self, entrevista_id: str, solicitante_id: str, resposta_texto: str) -> tuple[Optional[str], bool]:
        entrevista = self._buscar_entrevista_do_candidato(entrevista_id, solicitante_id)
        if entrevista.concluida:
            raise EntrevistaJaConcluida("Esta entrevista já foi concluída")

        vaga = self.vaga_repo.buscar(entrevista.vaga_id)
        if vaga is None:
            raise RecursoNaoEncontrado("Vaga não encontrada")

        pergunta_template = self.pergunta_repo.buscar_por_softskill(entrevista.memoria.softskill_atual())
        resultado = self.llm.gerar_pergunta(vaga, entrevista.memoria, pergunta_template, resposta_texto)

        entrevista.memoria = resultado.memoria_atualizada
        if resultado.concluida:
            entrevista.concluir()
        self.entrevista_repo.salvar(entrevista)

        return resultado.proxima_pergunta, resultado.concluida

    def obter_estado(self, entrevista_id: str, solicitante_id: str) -> Entrevista:
        """
        Usado pelos adapters de canal para reconstruir contexto — por exemplo
        um bot que reinicia no meio de uma conversa e precisa saber em que
        ponto da entrevista o candidato estava.
        """
        return self._buscar_entrevista_do_candidato(entrevista_id, solicitante_id)

    def gerar_resultado(self, entrevista_id: str, solicitante_id: str, papel_solicitante: str) -> Resultado:
        entrevista = self.entrevista_repo.buscar(entrevista_id)
        if entrevista is None:
            raise RecursoNaoEncontrado("Entrevista não encontrada")

        vaga = self.vaga_repo.buscar(entrevista.vaga_id)
        if vaga is None:
            raise RecursoNaoEncontrado("Vaga não encontrada")

        dono = entrevista.candidato_id == solicitante_id
        dona_da_vaga = papel_solicitante == "recrutador" and vaga.empresa_id == solicitante_id
        if not (dono or dona_da_vaga):
            raise AcessoNegado("Você não tem acesso a esta entrevista")

        resultado_existente = self.resultado_repo.buscar_por_entrevista(entrevista_id)
        if resultado_existente is not None:
            return resultado_existente

        resumo_ia = self.llm.gerar_resumo_resultado(vaga, entrevista.memoria)
        pontuacoes = {
            s.nome: s.pontuacao for s in entrevista.memoria.softskills if s.pontuacao is not None
        }
        resultado = Resultado(
            entrevista_id=entrevista_id,
            pontuacoes=pontuacoes,
            resumo=resumo_ia.resumo,
            recomendacao=resumo_ia.recomendacao,
        )
        self.resultado_repo.salvar(resultado)
        return resultado

    def _buscar_entrevista_do_candidato(self, entrevista_id: str, solicitante_id: str) -> Entrevista:
        entrevista = self.entrevista_repo.buscar(entrevista_id)
        if entrevista is None:
            raise RecursoNaoEncontrado("Entrevista não encontrada")
        if entrevista.candidato_id != solicitante_id:
            raise AcessoNegado("Você não tem acesso a esta entrevista")
        return entrevista
