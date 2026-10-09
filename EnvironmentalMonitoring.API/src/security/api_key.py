"""Validação de API key via header HTTP."""

import secrets

from fastapi import Header, HTTPException, status

from src.config import get_settings


def validate_api_key(
    apikey: str | None = Header(
        default=None,
        description="API key de acesso. Obrigatória.",
    ),
) -> None:
    """Valida API key recebida no header 'apikey'."""
    settings = get_settings()
    received_key = (apikey or "").encode("utf-8")
    expected_key = settings.api_key.encode("utf-8")

    if not apikey or not secrets.compare_digest(received_key, expected_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key inválida ou não informada.",
        )
