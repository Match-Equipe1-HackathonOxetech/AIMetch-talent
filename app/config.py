import os
 
 
class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///recrutamento.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
 
    # pool_pre_ping: antes de reusar uma conexão do pool, testa se ela ainda
    # está viva e reconecta se não estiver — evita o erro "SSL connection has
    # been closed unexpectedly" quando o Postgres (gerenciado ou não) derruba
    # conexões ociosas.
    # pool_recycle: descarta e recria conexões com mais de 280s, ficando na
    # frente de provedores que fecham conexões ociosas por volta dos 5min.
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
    }
 
    JWT_SECRET = os.environ.get("JWT_SECRET", "troque-esta-chave-em-producao")
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
    GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
 