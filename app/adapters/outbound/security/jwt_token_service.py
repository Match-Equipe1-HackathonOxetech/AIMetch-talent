from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import jwt

from app.ports.security_ports import ParDeTokens, TokenServicePort

ACCESS_TOKEN_VALIDADE_MINUTOS = 15
REFRESH_TOKEN_VALIDADE_DIAS = 7


class JWTTokenService(TokenServicePort):
    def __init__(self, secret: str, algoritmo: str = "HS256"):
        self.secret = secret
        self.algoritmo = algoritmo

    def emitir_par(self, usuario_id: str, role: str) -> ParDeTokens:
        agora = datetime.now(timezone.utc)

        access_payload = {
            "sub": usuario_id,
            "role": role,
            "type": "access",
            "iat": agora,
            "exp": agora + timedelta(minutes=ACCESS_TOKEN_VALIDADE_MINUTOS),
        }
        refresh_payload = {
            "sub": usuario_id,
            "role": role,
            "type": "refresh",
            "jti": uuid.uuid4().hex,  # identifica unicamente o refresh_token emitido
            "iat": agora,
            "exp": agora + timedelta(days=REFRESH_TOKEN_VALIDADE_DIAS),
        }

        access_token = jwt.encode(access_payload, self.secret, algorithm=self.algoritmo)
        refresh_token = jwt.encode(refresh_payload, self.secret, algorithm=self.algoritmo)
        return ParDeTokens(access_token=access_token, refresh_token=refresh_token)

    def decodificar_access_token(self, token: str) -> dict:
        payload = jwt.decode(token, self.secret, algorithms=[self.algoritmo])
        if payload.get("type") != "access":
            raise jwt.InvalidTokenError("Token não é um access_token")
        return payload

    def decodificar_refresh_token(self, token: str) -> dict:
        payload = jwt.decode(token, self.secret, algorithms=[self.algoritmo])
        if payload.get("type") != "refresh":
            raise jwt.InvalidTokenError("Token não é um refresh_token")
        return payload
