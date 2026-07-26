from flask import Blueprint, g, jsonify, request

from app.adapters.inbound.http.schemas import CriarEntrevistaSchema, ResponderEntrevistaSchema
from app.domain.services.entrevista_service import EntrevistaService


def criar_entrevista_blueprint(entrevista_service: EntrevistaService, requer_role, jwt_required) -> Blueprint:
    """
    Estas rotas são só tradução HTTP <-> EntrevistaService. A mesma lógica que
    roda aqui é a que, no futuro, um handler de bot do Telegram ou WhatsApp
    chamaria diretamente em cima do mesmo EntrevistaService — sem passar por
    Flask e sem duplicar nada do que está nos métodos do service.
    """
    bp = Blueprint("entrevistas", __name__)
    criar_schema = CriarEntrevistaSchema()
    responder_schema = ResponderEntrevistaSchema()

    @bp.route("/entrevistas", methods=["POST"])
    @requer_role("recrutado")
    def criar_entrevista():
        dados = criar_schema.load(request.get_json(silent=True) or {})
        entrevista_id, pergunta = entrevista_service.iniciar_entrevista(dados["candidato_id"], dados["vaga_id"])
        return jsonify({"entrevista_id": entrevista_id, "pergunta": pergunta}), 201

    @bp.route("/entrevistas/<entrevista_id>/respostas", methods=["POST"])
    @requer_role("recrutado")
    def responder(entrevista_id):
        dados = responder_schema.load(request.get_json(silent=True) or {})
        pergunta, concluida = entrevista_service.responder(entrevista_id, g.usuario_id, dados["resposta"])
        return jsonify({"pergunta": pergunta, "concluida": concluida})

    @bp.route("/entrevistas/<entrevista_id>", methods=["GET"])
    @requer_role("recrutado")
    def obter_estado(entrevista_id):
        entrevista = entrevista_service.obter_estado(entrevista_id, g.usuario_id)
        return jsonify({
            "id": entrevista.id,
            "vaga_id": entrevista.vaga_id,
            "status": entrevista.status,
            "memoria": entrevista.memoria.to_dict(),
        })

    @bp.route("/entrevistas/<entrevista_id>/resultado", methods=["POST"])
    @jwt_required
    def gerar_resultado(entrevista_id):
        # Tanto o candidato dono quanto a empresa dona da vaga podem disparar
        # a consolidação do resultado — por isso aqui só exigimos autenticação
        # (qualquer role); a checagem fina de "é o dono ou é a empresa da
        # vaga" é responsabilidade do domínio (EntrevistaService.gerar_resultado).
        resultado = entrevista_service.gerar_resultado(entrevista_id, g.usuario_id, g.role)
        return jsonify({
            "id": resultado.id,
            "entrevista_id": resultado.entrevista_id,
            "pontuacoes": resultado.pontuacoes,
            "resumo": resultado.resumo,
            "recomendacao": resultado.recomendacao,
        })

    return bp
