from flask import Blueprint, jsonify, request

from app.adapters.inbound.http.schemas import CriarCandidatoSchema
from app.domain.services.auth_service import AuthService


def criar_candidato_blueprint(auth_service: AuthService) -> Blueprint:
    bp = Blueprint("candidatos", __name__)
    schema = CriarCandidatoSchema()

    @bp.route("/candidatos", methods=["POST"])
    def criar_candidato():
        dados = schema.load(request.get_json(silent=True) or {})
        candidato = auth_service.registrar_candidato(dados["nome"], dados["email"], dados["senha"])
        return jsonify({"id": candidato.id, "nome": candidato.nome, "email": candidato.email}), 201

    return bp
