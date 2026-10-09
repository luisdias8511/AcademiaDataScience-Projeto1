"""Schemas para endpoints futuros de meteorologia."""

from pydantic import BaseModel, Field

from src.schemas.common import PageResponse, ParameterValueResponse

class WeatherEntryResponse(BaseModel):
    """Representa uma entrada de histórico meteorológico."""

    found: bool
    datetime: str
    index: None = None
    parameters: dict[str, ParameterValueResponse] = Field(default_factory=dict)


class WeatherHistoryResponse(BaseModel):
    """Representa a resposta completa de histórico meteorológico."""

    found: bool
    values: list[WeatherEntryResponse] = Field(default_factory=list)
    page: PageResponse
