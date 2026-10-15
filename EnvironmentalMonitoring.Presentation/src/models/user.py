"""Modelo de domínio para novo usuário."""

from dataclasses import dataclass


@dataclass
class NewUser:
    """Dados informados no formulário de cadastro (tabela Users).

    A senha é guardada em texto apenas até o momento do cadastro.
    No banco, a coluna PasswordHash deve receber o hash dela (implementação futura).
    """

    username: str
    password: str
    email: str
    cpf: str
    phone: str | None
    atribution: str
