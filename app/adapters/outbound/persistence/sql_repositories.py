"""
Implementações concretas das portas de persistência, usando SQLAlchemy.

Cada método faz a tradução ORM <-> entidade de domínio, então tudo que passa
por cima da linha desta camada (os services) só enxerga objetos de domínio
puros (app.domain.entities), nunca um *Model do SQLAlchemy.
"""
from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.adapters.outbound.persistence.models import (
    CandidatoModel,
    EmpresaModel,
    EntrevistaModel,
    PerguntaTemplateModel,
    RefreshTokenModel,
    ResultadoModel,
    VagaModel,
)
from app.domain.entities import (
    Candidato,
    Empresa,
    Entrevista,
    PerguntaTemplate,
    RefreshToken,
    Resultado,
    Vaga,
)
from app.domain.value_objects import Memoria
from app.ports.repositories import (
    CandidatoRepository,
    EmpresaRepository,
    EntrevistaRepository,
    PerguntaTemplateRepository,
    RefreshTokenRepository,
    ResultadoRepository,
    VagaRepository,
)


class SqlEmpresaRepository(EmpresaRepository):
    def __init__(self, session: Session):
        self.session = session

    def salvar(self, empresa: Empresa) -> None:
        modelo = self.session.get(EmpresaModel, empresa.id) or EmpresaModel(id=empresa.id)
        modelo.nome = empresa.nome
        modelo.email = empresa.email
        modelo.senha_hash = empresa.senha_hash
        self.session.add(modelo)
        self.session.commit()

    def buscar(self, empresa_id: str) -> Optional[Empresa]:
        modelo = self.session.get(EmpresaModel, empresa_id)
        return self._para_entidade(modelo) if modelo else None

    def buscar_por_email(self, email: str) -> Optional[Empresa]:
        modelo = self.session.query(EmpresaModel).filter_by(email=email).first()
        return self._para_entidade(modelo) if modelo else None

    @staticmethod
    def _para_entidade(modelo: EmpresaModel) -> Empresa:
        return Empresa(id=modelo.id, nome=modelo.nome, email=modelo.email, senha_hash=modelo.senha_hash)


class SqlCandidatoRepository(CandidatoRepository):
    def __init__(self, session: Session):
        self.session = session

    def salvar(self, candidato: Candidato) -> None:
        modelo = self.session.get(CandidatoModel, candidato.id) or CandidatoModel(id=candidato.id)
        modelo.nome = candidato.nome
        modelo.email = candidato.email
        modelo.senha_hash = candidato.senha_hash
        self.session.add(modelo)
        self.session.commit()

    def buscar(self, candidato_id: str) -> Optional[Candidato]:
        modelo = self.session.get(CandidatoModel, candidato_id)
        return self._para_entidade(modelo) if modelo else None

    def buscar_por_email(self, email: str) -> Optional[Candidato]:
        modelo = self.session.query(CandidatoModel).filter_by(email=email).first()
        return self._para_entidade(modelo) if modelo else None

    @staticmethod
    def _para_entidade(modelo: CandidatoModel) -> Candidato:
        return Candidato(id=modelo.id, nome=modelo.nome, email=modelo.email, senha_hash=modelo.senha_hash)


class SqlVagaRepository(VagaRepository):
    def __init__(self, session: Session):
        self.session = session

    def salvar(self, vaga: Vaga) -> None:
        modelo = self.session.get(VagaModel, vaga.id) or VagaModel(id=vaga.id)
        modelo.empresa_id = vaga.empresa_id
        modelo.titulo = vaga.titulo
        modelo.softskills_alvo = vaga.softskills_alvo
        self.session.add(modelo)
        self.session.commit()

    def buscar(self, vaga_id: str) -> Optional[Vaga]:
        modelo = self.session.get(VagaModel, vaga_id)
        if not modelo:
            return None
        return Vaga(
            id=modelo.id, empresa_id=modelo.empresa_id, titulo=modelo.titulo,
            softskills_alvo=modelo.softskills_alvo,
        )


class SqlPerguntaTemplateRepository(PerguntaTemplateRepository):
    def __init__(self, session: Session):
        self.session = session

    def buscar_por_softskill(self, softskill: Optional[str]) -> Optional[PerguntaTemplate]:
        if softskill is None:
            return None
        modelo = self.session.query(PerguntaTemplateModel).filter_by(softskill=softskill).first()
        if not modelo:
            return None
        return PerguntaTemplate(id=modelo.id, softskill=modelo.softskill, texto=modelo.texto)


class SqlEntrevistaRepository(EntrevistaRepository):
    def __init__(self, session: Session):
        self.session = session

    def salvar(self, entrevista: Entrevista) -> None:
        modelo = self.session.get(EntrevistaModel, entrevista.id) or EntrevistaModel(id=entrevista.id)
        modelo.candidato_id = entrevista.candidato_id
        modelo.vaga_id = entrevista.vaga_id
        modelo.memoria = entrevista.memoria.to_dict()
        modelo.status = entrevista.status
        modelo.criada_em = entrevista.criada_em
        self.session.add(modelo)
        self.session.commit()

    def buscar(self, entrevista_id: str) -> Optional[Entrevista]:
        modelo = self.session.get(EntrevistaModel, entrevista_id)
        if not modelo:
            return None
        return Entrevista(
            id=modelo.id,
            candidato_id=modelo.candidato_id,
            vaga_id=modelo.vaga_id,
            memoria=Memoria.from_dict(modelo.memoria),
            status=modelo.status,
            criada_em=modelo.criada_em,
        )


class SqlResultadoRepository(ResultadoRepository):
    def __init__(self, session: Session):
        self.session = session

    def salvar(self, resultado: Resultado) -> None:
        modelo = self.session.get(ResultadoModel, resultado.id) or ResultadoModel(id=resultado.id)
        modelo.entrevista_id = resultado.entrevista_id
        modelo.pontuacoes = resultado.pontuacoes
        modelo.resumo = resultado.resumo
        modelo.recomendacao = resultado.recomendacao
        self.session.add(modelo)
        self.session.commit()

    def buscar_por_entrevista(self, entrevista_id: str) -> Optional[Resultado]:
        modelo = self.session.query(ResultadoModel).filter_by(entrevista_id=entrevista_id).first()
        return self._para_entidade(modelo) if modelo else None

    def listar_por_vaga(self, vaga_id: str) -> list[Resultado]:
        modelos = (
            self.session.query(ResultadoModel)
            .join(EntrevistaModel, ResultadoModel.entrevista_id == EntrevistaModel.id)
            .filter(EntrevistaModel.vaga_id == vaga_id)
            .all()
        )
        return [self._para_entidade(m) for m in modelos]

    @staticmethod
    def _para_entidade(modelo: ResultadoModel) -> Resultado:
        return Resultado(
            id=modelo.id, entrevista_id=modelo.entrevista_id, pontuacoes=modelo.pontuacoes,
            resumo=modelo.resumo, recomendacao=modelo.recomendacao,
        )


class SqlRefreshTokenRepository(RefreshTokenRepository):
    def __init__(self, session: Session):
        self.session = session

    def salvar(self, refresh_token: RefreshToken) -> None:
        modelo = self.session.get(RefreshTokenModel, refresh_token.id) or RefreshTokenModel(id=refresh_token.id)
        modelo.usuario_id = refresh_token.usuario_id
        modelo.role = refresh_token.role
        modelo.token = refresh_token.token
        modelo.expira_em = refresh_token.expira_em
        modelo.revogado = refresh_token.revogado
        self.session.add(modelo)
        self.session.commit()

    def buscar_por_token(self, token: str) -> Optional[RefreshToken]:
        modelo = self.session.query(RefreshTokenModel).filter_by(token=token).first()
        if not modelo:
            return None
        return RefreshToken(
            id=modelo.id, usuario_id=modelo.usuario_id, role=modelo.role, token=modelo.token,
            expira_em=modelo.expira_em, revogado=modelo.revogado,
        )

    def revogar(self, token: str) -> None:
        modelo = self.session.query(RefreshTokenModel).filter_by(token=token).first()
        if modelo:
            modelo.revogado = True
            self.session.commit()
