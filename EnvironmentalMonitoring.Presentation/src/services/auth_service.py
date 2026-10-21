"""Serviço de autenticação (login) dos usuários da tabela Users.

Regras de segurança:
- A senha digitada é conferida com o hash PBKDF2 gravado em PasswordHash
  (src/security/password_hashing.py). A senha nunca é gravada nem logada, apenas comparada com o hash.
- Mensagem de erro GENÉRICA ("Usuário ou senha inválidos"): não revela se o
  usuário existe (evita enumeração de usuários).
- Quando o usuário não existe, o hash é calculado mesmo assim (hash "falso"),
  para que o tempo de resposta seja parecido nos dois casos (evita timing attack).
- Todas as tentativas ficam no log de auditoria (somente o username, nunca a senha).
"""
from typing import Any, Dict

from src.config import logger
from src.database.user_repository import UserRepository
from src.security.password_hashing import gerar_hash_senha, verificar_senha

# Hash "falso" gerado uma única vez, usado quando o usuário não existe
_HASH_FALSO = gerar_hash_senha("senha-inexistente-para-equalizar-tempo")


def authenticate(username: str, password: str,
                 repository: UserRepository | None = None) -> Dict[str, Any] | None:
    """Valida usuário e senha.

    Retorna {"id_usuario", "username", "atribution"} se o login for válido,
    ou None se usuário/senha estiverem incorretos.
    """
    username = (username or "").strip()
    if not username or not password:
        return None

    dados = (repository or UserRepository()).get_login_data(username)

    # Sempre executa a verificação (mesmo sem usuário) -> tempo de resposta parecido
    hash_gravado = dados["password_hash"] if dados else _HASH_FALSO
    senha_ok = verificar_senha(password, hash_gravado or _HASH_FALSO)

    if dados is None or not senha_ok:
        logger.warning("Tentativa de login inválida", extra={"username": username})
        return None

    logger.info("Login realizado com sucesso", extra={"usuario_id": dados["id_usuario"]})
    # Devolve somente o necessário para a sessão (o hash NÃO vai para a sessão)
    return {
        "id_usuario": dados["id_usuario"],
        "username": dados["username"],
        "atribution": dados["atribution"],
    }
