from flask import Blueprint, jsonify, request

from app.adapters.inbound.http.schemas import CriarEmpresaSchema
from app.domain.services.auth_service import AuthService


def criar_empresa_blueprint(auth_service: AuthService) -> Blueprint:
    bp = Blueprint("empresas", __name__)
    schema = CriarEmpresaSchema()

    @bp.route("/empresas", methods=["POST"])
    def criar_empresa():
        dados = schema.load(request.get_json(silent=True) or {})
        empresa = auth_service.registrar_empresa(dados["nome"], dados["email"], dados["senha"])
        return jsonify({"id": empresa.id, "nome": empresa.nome, "email": empresa.email}), 201

    return bp
