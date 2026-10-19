"""Modelo de domínio para novo usuário."""
from dataclasses import dataclass


@dataclass
class NewUser:
    """Dados informados no formulário de cadastro (tabela Users).

    Os valores ficam em texto aberto SOMENTE em memória, até o momento do cadastro.
    Antes de chegar ao banco, o serviço aplica a política LGPD (src/security/lgpd.py):
        - full_name -> hash SHA-256 (FullName)
        - cpf       -> hash SHA-256 irreversível (CpfHash)
        - email     -> criptografia Fernet (EmailCripto)
        - phone     -> criptografia Fernet (PhoneCripto)
        - password  -> hash PBKDF2-SHA256 com salt aleatório (PasswordHash)
    """
    username: str
    full_name: str
    password: str
    email: str
    cpf: str
    phone: str | None
    atribution: str
