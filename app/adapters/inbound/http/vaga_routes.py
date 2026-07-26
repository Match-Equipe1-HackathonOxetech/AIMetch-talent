from flask import Blueprint, g, jsonify, request

from app.adapters.inbound.http.schemas import CriarVagaSchema
from app.domain.services.vaga_service import VagaService


def criar_vaga_blueprint(vaga_service: VagaService, requer_role) -> Blueprint:
    bp = Blueprint("vagas", __name__)
    schema = CriarVagaSchema()

    @bp.route("/vagas", methods=["POST"])
    @requer_role("recrutador")
    def criar_vaga():
        dados = schema.load(request.get_json(silent=True) or {})
        vaga = vaga_service.criar_vaga(g.usuario_id, dados["titulo"], dados["softskills_alvo"])
        return jsonify({
            "id": vaga.id, "titulo": vaga.titulo, "softskills_alvo": vaga.softskills_alvo,
        }), 201

    @bp.route("/vagas/<vaga_id>/resultados", methods=["GET"])
    @requer_role("recrutador")
    def listar_resultados(vaga_id):
        resultados = vaga_service.listar_resultados(vaga_id, g.usuario_id)
        return jsonify([
            {
                "id": r.id,
                "entrevista_id": r.entrevista_id,
                "pontuacoes": r.pontuacoes,
                "resumo": r.resumo,
                "recomendacao": r.recomendacao,
            }
            for r in resultados
        ])

    return bp
    
@bp.route("/empresas/<empresa_id>/vagas", methods=["GET"])
@requer_role("recrutador")
def listar_vagas_empresa(empresa_id):
    vagas = vaga_service.listar_vagas_empresa(
        empresa_id,
        g.usuario_id,
    )

    return jsonify([
        {
            "id": vaga.id,
            "titulo": vaga.titulo,
            "softskills_alvo": vaga.softskills_alvo,
        }
        for vaga in vagas
    ])
