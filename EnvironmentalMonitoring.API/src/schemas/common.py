"""Schemas comuns para respostas da API."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_serializer


class ErrorResponse(BaseModel):
    """Representa uma resposta padronizada de erro."""

    detail: str = Field(..., description="Mensagem de erro para o consumidor.")


ERROR_RESPONSES: dict[int | str, dict[str, object]] = {
    401: {"model": ErrorResponse, "description": "API key inválida ou não informada."},
    404: {"model": ErrorResponse, "description": "Localização não encontrada."},
    422: {"model": ErrorResponse, "description": "Parâmetro inválido."},
    500: {"model": ErrorResponse, "description": "Erro interno ao consultar os dados."},
}


class ApiStatusResponse(BaseModel):
    """Representa um retorno simples de status da API."""

    status: str = Field(..., description="Estado atual da API.")
    timestamp: datetime = Field(..., description="Data e hora de referência.")


class PageResponse(BaseModel):
    """Representa metadados de paginação da resposta."""

    totalElements: int = Field(..., ge=0)
    totalPages: int = Field(..., ge=0)
    pageNumber: int = Field(..., ge=0)
    size: int = Field(..., gt=0)


class ParameterValueResponse(BaseModel):
    """Representa um valor de parâmetro no formato da API."""

    shortcode: None = None
    name: str
    unit: str | None
    found: bool
    value: Decimal
    confidence: None = None
    index: None = None

    @field_serializer("value")
    def serialize_value(self, value: Decimal) -> float:
        """Serializa o valor decimal como número JSON."""
        return float(value)
