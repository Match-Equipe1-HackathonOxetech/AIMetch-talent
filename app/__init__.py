"""
Composition root da aplicação.

É o único lugar do projeto que conhece TODAS as camadas ao mesmo tempo:
instancia os adapters concretos (Gemini, SQLAlchemy, JWT), injeta-os nos
services de domínio e registra os blueprints Flask. Os services nunca
instanciam suas próprias dependências — tudo chega pronto no construtor.
"""
from flask import Flask

from app.adapters.inbound.http.auth_routes import criar_auth_blueprint
from app.adapters.inbound.http.candidato_routes import criar_candidato_blueprint
from app.adapters.inbound.http.decorators import criar_decoradores_auth
from app.adapters.inbound.http.empresa_routes import criar_empresa_blueprint
from app.adapters.inbound.http.entrevista_routes import criar_entrevista_blueprint
from app.adapters.inbound.http.error_handlers import registrar_error_handlers
from app.adapters.inbound.http.vaga_routes import criar_vaga_blueprint
from app.adapters.outbound.llm.gemini_adapter import GeminiAdapter
from app.adapters.outbound.persistence.sql_repositories import (
    SqlCandidatoRepository,
    SqlEmpresaRepository,
    SqlEntrevistaRepository,
    SqlPerguntaTemplateRepository,
    SqlRefreshTokenRepository,
    SqlResultadoRepository,
    SqlVagaRepository,
)
from app.adapters.outbound.security.jwt_token_service import JWTTokenService
from app.adapters.outbound.security.password_hasher import WerkzeugPasswordHasher
from app.config import Config
from app.domain.services.auth_service import AuthService
from app.domain.services.entrevista_service import EntrevistaService
from app.domain.services.vaga_service import VagaService
from app.extensions import db


def criar_app(config_class: type = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    registrar_error_handlers(app)

    with app.app_context():
        db.create_all()

        # --- Adapters de saída (implementações concretas das portas) ---
        empresa_repo = SqlEmpresaRepository(db.session)
        candidato_repo = SqlCandidatoRepository(db.session)
        vaga_repo = SqlVagaRepository(db.session)
        pergunta_repo = SqlPerguntaTemplateRepository(db.session)
        entrevista_repo = SqlEntrevistaRepository(db.session)
        resultado_repo = SqlResultadoRepository(db.session)
        refresh_token_repo = SqlRefreshTokenRepository(db.session)

        password_hasher = WerkzeugPasswordHasher()
        token_service = JWTTokenService(secret=app.config["JWT_SECRET"])
        llm = GeminiAdapter(api_key=app.config["GEMINI_API_KEY"], modelo=app.config["GEMINI_MODEL"])

        # --- Services de domínio (só recebem portas, nunca implementações) ---
        auth_service = AuthService(empresa_repo, candidato_repo, refresh_token_repo, password_hasher, token_service)
        vaga_service = VagaService(vaga_repo, resultado_repo)
        entrevista_service = EntrevistaService(entrevista_repo, vaga_repo, pergunta_repo, resultado_repo, llm)

        # --- Adapters de entrada (rotas Flask) ---
        jwt_required, requer_role = criar_decoradores_auth(token_service)

        app.register_blueprint(criar_empresa_blueprint(auth_service))
        app.register_blueprint(criar_candidato_blueprint(auth_service))
        app.register_blueprint(criar_auth_blueprint(auth_service))
        app.register_blueprint(criar_vaga_blueprint(vaga_service, requer_role))
        app.register_blueprint(criar_entrevista_blueprint(entrevista_service, requer_role, jwt_required))

    return app
