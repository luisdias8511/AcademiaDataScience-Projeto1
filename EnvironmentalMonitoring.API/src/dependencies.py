"""Dependências reutilizáveis da aplicação FastAPI."""

from fastapi import Header

from src.security.api_key import validate_api_key


def require_api_key(apikey: str | None = Header(default=None)) -> None:
    """Dependência simples para exigir API key nos endpoints."""
    validate_api_key(apikey=apikey)
