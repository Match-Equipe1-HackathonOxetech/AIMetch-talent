from marshmallow import Schema, fields, validate


class CriarEmpresaSchema(Schema):
    nome = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    email = fields.Email(required=True)
    senha = fields.Str(required=True, validate=validate.Length(min=8))


class CriarCandidatoSchema(Schema):
    nome = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    email = fields.Email(required=True)
    senha = fields.Str(required=True, validate=validate.Length(min=8))


class LoginSchema(Schema):
    email = fields.Email(required=True)
    senha = fields.Str(required=True)


class RefreshSchema(Schema):
    refresh_token = fields.Str(required=True)


class CriarVagaSchema(Schema):
    titulo = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    softskills_alvo = fields.List(fields.Str(), required=True, validate=validate.Length(min=1))


class CriarEntrevistaSchema(Schema):
    candidato_id = fields.Str(required=True)
    vaga_id = fields.Str(required=True)


class ResponderEntrevistaSchema(Schema):
    resposta = fields.Str(required=True, validate=validate.Length(min=1))
