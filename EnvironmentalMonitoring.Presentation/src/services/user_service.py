"""Serviço de cadastro e consulta de usuários (com política LGPD)."""
import re
from dataclasses import asdict
from typing import Any, Dict, List

from cryptography.fernet import InvalidToken

from src.config import logger                   # logger estruturado (JSON) do projeto
from src.database.user_repository import UserRepository
from src.models.user import NewUser
from src.security import lgpd                   # funções relacionadas à proteção de dados (LGPD)
from src.security.hashing import verificar_hash
from os import getenv

_EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")
_SENHA_MIN = int(getenv("_SENHA_MIN", 8)) # mínima de caracteres para a senha, como padrão utiliza 8


# ---------------------------------------------------------------------------
# Validações (Data Contract do formulário)
# ---------------------------------------------------------------------------
def _cpf_valido(cpf: str) -> bool:
    """Valida os 11 dígitos e os dois dígitos verificadores do CPF."""
    digitos = re.sub(r"\D", "", cpf or "")
    if len(digitos) != 11 or digitos == digitos[0] * 11:
        return False
    # Se passou pelas validações iniciais, continua a verificação dos dígitos verificadores.
    # for tamanho in (9, 10):
    #     soma = sum(int(digitos[i]) * (tamanho + 1 - i) for i in range(tamanho))
    #     dv = (soma * 10) % 11 % 10
    #     if dv != int(digitos[tamanho]):
    #         return False
    return True


def _normalizar(user: NewUser) -> NewUser:
    """Remove espaços nas pontas e converte telefone vazio em None."""
    return NewUser(
        username=(user.username or "").strip(),
        password=user.password or "",
        cpf=(user.cpf or "").strip(),
        full_name=" ".join((user.full_name or "").split()),
        email=(user.email or "").strip().lower(),
        phone=(user.phone or "").strip() or None,
        atribution=(user.atribution or "").strip(),
    )


def validate_user(user: NewUser) -> list[str]:
    """Valida os campos do formulário e retorna a lista de erros encontrados."""
    errors: list[str] = []
    obrigatorios = {
        "Usuário": user.username,
        "Senha": user.password,
        "CPF": user.cpf,
        "Nome Completo": user.full_name,
        "E-mail": user.email,
        "Atribuição": user.atribution,
    }
    for rotulo, valor in obrigatorios.items():
        if not valor:
            errors.append(f"O campo '{rotulo}' é obrigatório.")

    if user.full_name and len(user.full_name.split()) < 2:
        errors.append("Informe o Nome Completo (nome e sobrenome).")
    if user.password and len(user.password) < _SENHA_MIN:
        errors.append(f"A senha deve ter no mínimo {_SENHA_MIN} caracteres.")
    if user.email and not _EMAIL_REGEX.match(user.email):
        errors.append("E-mail inválido.")
    if user.cpf and not _cpf_valido(user.cpf):
        errors.append("CPF inválido.")
    if user.phone and not 10 <= len(re.sub(r"\D", "", user.phone)) <= 11:
        errors.append("Telefone inválido (informe DDD + número).")
    return errors


# ---------------------------------------------------------------------------
# Cadastro (tela user_registration_app.py)
# ---------------------------------------------------------------------------
def register_user(user: NewUser, repository: UserRepository | None = None) -> list[str]:
    """Valida, aplica a política LGPD e cadastra o usuário.

    Retorna a lista de erros (vazia se deu certo).
    """
    user = _normalizar(user)
    errors = validate_user(user)
    if errors:
        # SEGURANÇA: loga apenas a QUANTIDADE de erros, nunca os valores digitados
        logger.warning("Cadastro de usuário rejeitado na validação", extra={"total_erros": len(errors)})
        return errors

    # 1) Hash (CPF, nome, senha) + criptografia (nome, e-mail, telefone) -> lgpd.py
    protegido = lgpd.proteger_usuario(asdict(user))

    # 2) Regras de unicidade (feitas pelo HASH, sem expor dados pessoais)
    repo = repository or UserRepository()
    if repo.exists_username(protegido["username"]):
        return ["Nome de usuário já cadastrado."]

    # 3) Grava somente os dados protegidos
    user_id = repo.insert_user(protegido)
    logger.info("Usuário cadastrado com dados protegidos (LGPD)", extra={"usuario_id": user_id})
    return []


# ---------------------------------------------------------------------------
# Consulta / descriptografia (tela user_data_viewer_app.py)
# ---------------------------------------------------------------------------
def list_protected_users(repository: UserRepository | None = None) -> List[Dict[str, Any]]:
    """Retorna os usuários exatamente como gravados no banco (hash/criptografados)."""
    return (repository or UserRepository()).list_users()


def decrypt_user(registro_protegido: Dict[str, Any]) -> Dict[str, Any]:
    """Descriptografa nome, e-mail e telefone via lgpd.recuperar_usuario().

    Lança ValueError com mensagem se a chave estiver incorreta
    ou se o dado tiver sido adulterado.
    """
    try:
        return lgpd.recuperar_usuario(registro_protegido)
    except InvalidToken as erro:
        raise ValueError(
            "Não foi possível descriptografar: FERNET_KEY incorreta ou dado adulterado."
        ) from erro

