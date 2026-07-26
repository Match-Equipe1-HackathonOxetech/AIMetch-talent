from __future__ import annotations

from datetime import datetime, timedelta

from app.domain.entities import Candidato, Empresa, RefreshToken
from app.domain.exceptions import CredenciaisInvalidas, EmailJaCadastrado, TokenInvalido
from app.ports.repositories import CandidatoRepository, EmpresaRepository, RefreshTokenRepository
from app.ports.security_ports import ParDeTokens, PasswordHasherPort, TokenServicePort

REFRESH_TOKEN_VALIDADE_DIAS = 7


class AuthService:
    def __init__(
        self,
        empresa_repo: EmpresaRepository,
        candidato_repo: CandidatoRepository,
        refresh_token_repo: RefreshTokenRepository,
        password_hasher: PasswordHasherPort,
        token_service: TokenServicePort,
    ):
        self.empresa_repo = empresa_repo
        self.candidato_repo = candidato_repo
        self.refresh_token_repo = refresh_token_repo
        self.password_hasher = password_hasher
        self.token_service = token_service

    def registrar_empresa(self, nome: str, email: str, senha: str) -> Empresa:
        if self.empresa_repo.buscar_por_email(email) is not None:
            raise EmailJaCadastrado("Já existe uma empresa cadastrada com este email")
        empresa = Empresa(nome=nome, email=email, senha_hash=self.password_hasher.gerar_hash(senha))
        self.empresa_repo.salvar(empresa)
        return empresa

    def registrar_candidato(self, nome: str, email: str, senha: str) -> Candidato:
        if self.candidato_repo.buscar_por_email(email) is not None:
            raise EmailJaCadastrado("Já existe um candidato cadastrado com este email")
        candidato = Candidato(nome=nome, email=email, senha_hash=self.password_hasher.gerar_hash(senha))
        self.candidato_repo.salvar(candidato)
        return candidato

    def login(self, email: str, senha: str) -> ParDeTokens:
        empresa = self.empresa_repo.buscar_por_email(email)
        if empresa is not None and self.password_hasher.verificar(senha, empresa.senha_hash):
            return self._emitir_e_registrar(empresa.id, "recrutador")

        candidato = self.candidato_repo.buscar_por_email(email)
        if candidato is not None and self.password_hasher.verificar(senha, candidato.senha_hash):
            return self._emitir_e_registrar(candidato.id, "recrutado")

        raise CredenciaisInvalidas("Email ou senha inválidos")

    def refresh(self, refresh_token: str) -> ParDeTokens:
        registro = self.refresh_token_repo.buscar_por_token(refresh_token)
        if registro is None or registro.revogado or registro.expira_em < datetime.utcnow():
            raise TokenInvalido("Refresh token inválido ou expirado")

        try:
            self.token_service.decodificar_refresh_token(refresh_token)
        except Exception as exc:  # assinatura/expiração inválida
            raise TokenInvalido("Refresh token inválido ou expirado") from exc

        # Rotaciona o refresh_token: revoga o antigo e emite um par novo.
        self.refresh_token_repo.revogar(refresh_token)
        return self._emitir_e_registrar(registro.usuario_id, registro.role)

    def logout(self, refresh_token: str) -> None:
        self.refresh_token_repo.revogar(refresh_token)

    def _emitir_e_registrar(self, usuario_id: str, role: str) -> ParDeTokens:
        par = self.token_service.emitir_par(usuario_id, role)
        registro = RefreshToken(
            usuario_id=usuario_id,
            role=role,
            token=par.refresh_token,
            expira_em=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_VALIDADE_DIAS),
        )
        self.refresh_token_repo.salvar(registro)
        return par
