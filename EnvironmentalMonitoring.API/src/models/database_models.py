"""Modelos internos de dados retornados do banco."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class Station:
    """Representa uma estação cadastrada no banco."""

    id: int
    code: str
    name: str
    latitude: Decimal
    longitude: Decimal


@dataclass(frozen=True)
class ParameterCategory:
    """Representa uma categoria de parâmetro."""

    id: int
    code: str
    name: str


@dataclass(frozen=True)
class Parameter:
    """Representa um parâmetro de medição."""

    id: int
    code: str
    code_api: str
    name: str
    unit: str | None
    category: ParameterCategory


@dataclass(frozen=True)
class ReadingValue:
    """Representa um valor associado a um parâmetro."""

    parameter: Parameter
    value: Decimal


@dataclass(frozen=True)
class Reading:
    """Representa uma leitura completa em um instante do tempo."""

    id: int
    station: Station
    timestamp: datetime
    values: tuple[ReadingValue, ...]


@dataclass(frozen=True)
class StationRecord:
    """Representa uma estação retornada por consulta de coordenadas."""

    id: int
    code: str
    name: str
    latitude: Decimal
    longitude: Decimal


@dataclass(frozen=True)
class ParameterValueRecord:
    """Representa valor de parâmetro retornado em consulta histórica."""

    code_api: str
    name: str
    unit: str | None
    value: Decimal


@dataclass(frozen=True)
class ReadingRecord:
    """Representa leitura histórica com valores associados."""

    id: int
    timestamp: datetime
    values: tuple[ParameterValueRecord, ...]
