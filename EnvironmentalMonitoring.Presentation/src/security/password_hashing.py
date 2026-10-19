"""
HASH DE SENHAS (complemento à política LGPD)
============================================
Senha NÃO pode ser criptografada (reversível) nem receber um SHA-256 simples:
usa-se um algoritmo LENTO e com salt aleatório por usuário, para dificultar
ataques de força bruta/dicionário caso o banco vaze.

Algoritmo: PBKDF2-HMAC-SHA256 (biblioteca padrão - hashlib), 600.000 iterações.
Formato gravado na coluna PasswordHash:
    pbkdf2_sha256$<iteracoes>$<salt_base64>$<hash_base64>
"""
import base64
import hashlib
import hmac
import os
from typing import Optional

ALGORITMO = "pbkdf2_sha256"
ITERACOES = 600_000
TAMANHO_SALT = 16  # bytes


def gerar_hash_senha(senha: Optional[str]) -> Optional[str]:
    """Gera o hash da senha (com salt aleatório). Cada chamada gera um resultado diferente."""
    if not senha:
        return None
    salt = os.urandom(TAMANHO_SALT)
    derivado = hashlib.pbkdf2_hmac("sha256", senha.encode("utf-8"), salt, ITERACOES)
    return "$".join([
        ALGORITMO,
        str(ITERACOES),
        base64.b64encode(salt).decode("ascii"),
        base64.b64encode(derivado).decode("ascii"),
    ])


def verificar_senha(senha: str, hash_armazenado: str) -> bool:
    """Confere se a senha informada corresponde ao hash gravado (uso futuro: login)."""
    try:
        algoritmo, iteracoes, salt_b64, hash_b64 = hash_armazenado.split("$")
        if algoritmo != ALGORITMO:
            return False
        derivado = hashlib.pbkdf2_hmac(
            "sha256", senha.encode("utf-8"), base64.b64decode(salt_b64), int(iteracoes)
        )
        # compare_digest evita ataques de tempo (timing attack)
        return hmac.compare_digest(derivado, base64.b64decode(hash_b64))
    except (ValueError, AttributeError):
        return False
