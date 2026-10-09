"""Schemas para endpoints futuros de qualidade da água."""

from pydantic import BaseModel, Field

from src.schemas.common import PageResponse, ParameterValueResponse

class WaterEntryResponse(BaseModel):
    """Representa uma entrada de histórico de qualidade da água."""

    datetime: str
    pollutants: dict[str, ParameterValueResponse] = Field(default_factory=dict)
    index: None = None
    found: bool


class WaterHistoryResponse(BaseModel):
    """Representa a resposta completa de histórico hídrico."""

    found: bool
    values: list[WaterEntryResponse] = Field(default_factory=list)
    page: PageResponse
