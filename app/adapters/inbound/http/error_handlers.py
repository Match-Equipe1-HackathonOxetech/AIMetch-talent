"""
Tradução de exceções de domínio em respostas HTTP. Mantém as rotas limpas —
elas não precisam de try/except para cada tipo de erro de negócio.
"""
from flask import jsonify
from marshmallow import ValidationError

from app.domain.exceptions import (
    AcessoNegado,
    CredenciaisInvalidas,
    DomainError,
    EmailJaCadastrado,
    EntrevistaJaConcluida,
    RecursoNaoEncontrado,
    TokenInvalido,
)

_STATUS_POR_EXCECAO = {
    RecursoNaoEncontrado: 404,
    AcessoNegado: 403,
    CredenciaisInvalidas: 401,
    TokenInvalido: 401,
    EmailJaCadastrado: 409,
    EntrevistaJaConcluida: 409,
}


def registrar_error_handlers(app):
    @app.errorhandler(ValidationError)
    def _validacao(erro: ValidationError):
        return jsonify({"erro": "Dados inválidos", "detalhes": erro.messages}), 400

    @app.errorhandler(DomainError)
    def _dominio(erro: DomainError):
        status = _STATUS_POR_EXCECAO.get(type(erro), 400)
        return jsonify({"erro": str(erro)}), status
