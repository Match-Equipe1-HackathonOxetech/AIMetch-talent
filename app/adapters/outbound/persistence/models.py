"""
Modelos SQLAlchemy. Espelham as entidades de domínio, mas são um detalhe de
implementação do adapter de persistência — o domínio nunca importa este
módulo. A tradução ORM <-> entidade de domínio acontece em
sql_repositories.py.
"""
from datetime import datetime

from app.extensions import db


class EmpresaModel(db.Model):
    __tablename__ = "empresas"

    id = db.Column(db.String(32), primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True, index=True)
    senha_hash = db.Column(db.String(255), nullable=False)

    vagas = db.relationship("VagaModel", backref="empresa", lazy=True)


class CandidatoModel(db.Model):
    __tablename__ = "candidatos"

    id = db.Column(db.String(32), primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True, index=True)
    senha_hash = db.Column(db.String(255), nullable=False)


class VagaModel(db.Model):
    __tablename__ = "vagas"

    id = db.Column(db.String(32), primary_key=True)
    empresa_id = db.Column(db.String(32), db.ForeignKey("empresas.id"), nullable=False)
    titulo = db.Column(db.String(200), nullable=False)
    softskills_alvo = db.Column(db.JSON, nullable=False)  # list[str]


class PerguntaTemplateModel(db.Model):
    __tablename__ = "perguntas_template"

    id = db.Column(db.String(32), primary_key=True)
    softskill = db.Column(db.String(100), nullable=False, index=True)
    texto = db.Column(db.Text, nullable=False)


class EntrevistaModel(db.Model):
    __tablename__ = "entrevistas"

    id = db.Column(db.String(32), primary_key=True)
    candidato_id = db.Column(db.String(32), db.ForeignKey("candidatos.id"), nullable=False)
    vaga_id = db.Column(db.String(32), db.ForeignKey("vagas.id"), nullable=False)
    memoria = db.Column(db.JSON, nullable=False)  # Memoria.to_dict()
    status = db.Column(db.String(20), nullable=False, default="em_andamento")
    criada_em = db.Column(db.DateTime, default=datetime.utcnow)


class ResultadoModel(db.Model):
    __tablename__ = "resultados"

    id = db.Column(db.String(32), primary_key=True)
    entrevista_id = db.Column(db.String(32), db.ForeignKey("entrevistas.id"), nullable=False, unique=True)
    pontuacoes = db.Column(db.JSON, nullable=False)  # dict[str, float]
    resumo = db.Column(db.Text, nullable=False)
    recomendacao = db.Column(db.Text, nullable=False)


class RefreshTokenModel(db.Model):
    __tablename__ = "refresh_tokens"

    id = db.Column(db.String(32), primary_key=True)
    usuario_id = db.Column(db.String(32), nullable=False, index=True)
    role = db.Column(db.String(20), nullable=False)
    token = db.Column(db.String(500), nullable=False, unique=True, index=True)
    expira_em = db.Column(db.DateTime, nullable=False)
    revogado = db.Column(db.Boolean, nullable=False, default=False)
