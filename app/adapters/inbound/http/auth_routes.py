from flask import Blueprint, jsonify, request

from app.adapters.inbound.http.schemas import LoginSchema, RefreshSchema
from app.domain.services.auth_service import AuthService


def criar_auth_blueprint(auth_service: AuthService) -> Blueprint:
    bp = Blueprint("auth", __name__)
    login_schema = LoginSchema()
    refresh_schema = RefreshSchema()

    @bp.route("/login", methods=["POST"])
    def login():
        dados = login_schema.load(request.get_json(silent=True) or {})
        par = auth_service.login(dados["email"], dados["senha"])
        return jsonify({"access_token": par.access_token, "refresh_token": par.refresh_token})

    @bp.route("/refresh", methods=["POST"])
    def refresh():
        dados = refresh_schema.load(request.get_json(silent=True) or {})
        par = auth_service.refresh(dados["refresh_token"])
        return jsonify({"access_token": par.access_token, "refresh_token": par.refresh_token})

    @bp.route("/logout", methods=["POST"])
    def logout():
        dados = refresh_schema.load(request.get_json(silent=True) or {})
        auth_service.logout(dados["refresh_token"])
        return jsonify({"mensagem": "Logout realizado"})

    return bp
