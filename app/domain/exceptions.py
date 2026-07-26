class DomainError(Exception):
    """Base de todos os erros de negócio. Adapters HTTP traduzem isso em status codes."""


class RecursoNaoEncontrado(DomainError):
    pass


class AcessoNegado(DomainError):
    pass


class CredenciaisInvalidas(DomainError):
    pass


class EmailJaCadastrado(DomainError):
    pass


class TokenInvalido(DomainError):
    pass


class EntrevistaJaConcluida(DomainError):
    pass
