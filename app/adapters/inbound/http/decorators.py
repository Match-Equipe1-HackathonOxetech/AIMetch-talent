"""
Decorators HTTP de autenticação. Ficam no adapter de entrada, não no domínio:
o que eles fazem é 100% relacionado a "como o HTTP carrega credenciais"
(header Authorization), algo que um handler de bot do Telegram/WhatsApp
resolveria de outra forma (ex.: token guardado na sessão da conversa).
"""
from functools import wraps

import jwt as pyjwt
from flask import g, jsonify, request

from app.ports.security_ports import TokenServicePort


def criar_decoradores_auth(token_service: TokenServicePort):
    def jwt_required(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                return jsonify({"erro": "Token de acesso ausente"}), 401

            token = auth_header.split(" ", 1)[1]
            try:
                payload = token_service.decodificar_access_token(token)
            except pyjwt.ExpiredSignatureError:
                return jsonify({"erro": "Token expirado"}), 401
            except pyjwt.InvalidTokenError:
                return jsonify({"erro": "Token inválido"}), 401

            g.usuario_id = payload["sub"]
            g.role = payload["role"]
            return f(*args, **kwargs)

        return wrapper

    def requer_role(role_esperada: str):
        def decorator(f):
            @jwt_required
            @wraps(f)
            def wrapper(*args, **kwargs):
                if g.role != role_esperada:
                    return jsonify({"erro": "Acesso negado para este papel"}), 403
                return f(*args, **kwargs)

            return wrapper

        return decorator

    return jwt_required, requer_role
