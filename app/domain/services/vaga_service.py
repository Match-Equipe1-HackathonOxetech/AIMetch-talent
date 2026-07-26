from __future__ import annotations

from app.domain.entities import Resultado, Vaga
from app.domain.exceptions import AcessoNegado, RecursoNaoEncontrado
from app.ports.repositories import ResultadoRepository, VagaRepository


class VagaService:
    def __init__(self, vaga_repo: VagaRepository, resultado_repo: ResultadoRepository):
        self.vaga_repo = vaga_repo
        self.resultado_repo = resultado_repo

    def criar_vaga(self, empresa_id: str, titulo: str, softskills_alvo: list[str]) -> Vaga:
        vaga = Vaga(empresa_id=empresa_id, titulo=titulo, softskills_alvo=softskills_alvo)
        self.vaga_repo.salvar(vaga)
        return vaga

    def listar_resultados(self, vaga_id: str, solicitante_id: str) -> list[Resultado]:
        vaga = self.vaga_repo.buscar(vaga_id)
        if vaga is None:
            raise RecursoNaoEncontrado("Vaga não encontrada")
        if vaga.empresa_id != solicitante_id:
            raise AcessoNegado("Você não tem acesso aos resultados desta vaga")
        return self.resultado_repo.listar_por_vaga(vaga_id)
