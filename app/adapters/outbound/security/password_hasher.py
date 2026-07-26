from werkzeug.security import check_password_hash, generate_password_hash

from app.ports.security_ports import PasswordHasherPort


class WerkzeugPasswordHasher(PasswordHasherPort):
    def gerar_hash(self, senha_texto: str) -> str:
        return generate_password_hash(senha_texto)

    def verificar(self, senha_texto: str, senha_hash: str) -> bool:
        return check_password_hash(senha_hash, senha_texto)
