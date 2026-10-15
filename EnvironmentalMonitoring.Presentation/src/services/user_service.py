"""Serviço de cadastro de usuários."""

from src.database.user_repository import UserRepository
from src.models.user import NewUser


def validate_user(user: NewUser) -> list[str]:
    """Valida os campos do formulário e retorna a lista de erros encontrados."""
    # TODO: implementar as validações (campos obrigatórios, e-mail, CPF, etc.).
    return []


def register_user(user: NewUser) -> list[str]:
    """Valida e cadastra o usuário. Retorna a lista de erros (vazia se deu certo)."""
    errors = validate_user(user)
    if errors:
        return errors

    UserRepository().insert_user(user)
    return []
