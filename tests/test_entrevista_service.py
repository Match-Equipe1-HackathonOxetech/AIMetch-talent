import pytest

from app.domain.entities import Vaga
from app.domain.exceptions import AcessoNegado, EntrevistaJaConcluida, RecursoNaoEncontrado
from app.domain.services.entrevista_service import EntrevistaService
from tests.fakes import (
    FakeEntrevistaRepository,
    FakeLLMPort,
    FakePerguntaTemplateRepository,
    FakeResultadoRepository,
    FakeVagaRepository,
)


@pytest.fixture
def service():
    vaga_repo = FakeVagaRepository()
    vaga_repo.salvar(Vaga(id="vaga-1", empresa_id="empresa-1", titulo="Dev Backend",
                          softskills_alvo=["comunicacao", "trabalho_em_equipe"]))
    return EntrevistaService(
        entrevista_repo=FakeEntrevistaRepository(),
        vaga_repo=vaga_repo,
        pergunta_repo=FakePerguntaTemplateRepository(),
        resultado_repo=FakeResultadoRepository(),
        llm=FakeLLMPort(),
    )


def test_iniciar_entrevista_retorna_primeira_pergunta(service):
    entrevista_id, pergunta = service.iniciar_entrevista("candidato-1", "vaga-1")

    assert entrevista_id
    assert "comunicacao" in pergunta


def test_iniciar_entrevista_com_vaga_inexistente_lanca_erro(service):
    with pytest.raises(RecursoNaoEncontrado):
        service.iniciar_entrevista("candidato-1", "vaga-inexistente")


def test_responder_avanca_para_proxima_softskill(service):
    entrevista_id, _ = service.iniciar_entrevista("candidato-1", "vaga-1")

    pergunta, concluida = service.responder(entrevista_id, "candidato-1", "Minha resposta sobre comunicação")

    assert concluida is False
    assert "trabalho_em_equipe" in pergunta


def test_entrevista_conclui_apos_todas_softskills_avaliadas(service):
    entrevista_id, _ = service.iniciar_entrevista("candidato-1", "vaga-1")
    service.responder(entrevista_id, "candidato-1", "Resposta 1")
    _, concluida = service.responder(entrevista_id, "candidato-1", "Resposta 2")

    assert concluida is True


def test_responder_apos_conclusao_lanca_erro(service):
    entrevista_id, _ = service.iniciar_entrevista("candidato-1", "vaga-1")
    service.responder(entrevista_id, "candidato-1", "Resposta 1")
    service.responder(entrevista_id, "candidato-1", "Resposta 2")

    with pytest.raises(EntrevistaJaConcluida):
        service.responder(entrevista_id, "candidato-1", "Resposta extra")


def test_outro_candidato_nao_acessa_entrevista_alheia(service):
    entrevista_id, _ = service.iniciar_entrevista("candidato-1", "vaga-1")

    with pytest.raises(AcessoNegado):
        service.responder(entrevista_id, "candidato-2", "Tentando responder por outra pessoa")


def test_gerar_resultado_consolida_pontuacoes(service):
    entrevista_id, _ = service.iniciar_entrevista("candidato-1", "vaga-1")
    service.responder(entrevista_id, "candidato-1", "Resposta 1")
    service.responder(entrevista_id, "candidato-1", "Resposta 2")

    resultado = service.gerar_resultado(entrevista_id, "candidato-1", "recrutado")

    assert resultado.pontuacoes == {"comunicacao": 8.0, "trabalho_em_equipe": 8.0}
    assert resultado.recomendacao == "Recomendado"


def test_recrutador_de_outra_vaga_nao_acessa_resultado(service):
    entrevista_id, _ = service.iniciar_entrevista("candidato-1", "vaga-1")
    service.responder(entrevista_id, "candidato-1", "Resposta 1")
    service.responder(entrevista_id, "candidato-1", "Resposta 2")

    with pytest.raises(AcessoNegado):
        service.gerar_resultado(entrevista_id, "empresa-2", "recrutador")
