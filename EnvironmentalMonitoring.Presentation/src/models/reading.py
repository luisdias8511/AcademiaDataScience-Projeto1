"""Modelo de domínio para Leituras de Dados Ambientais."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from src.models.reading_value import ReadingValue


@dataclass(frozen=True, slots=True)
class Reading:
    """Representa uma leitura de dados ambientais de uma estação em um momento específico.
    
    Reading agrupa múltiplos ReadingValue obtidos simultaneamente em uma estação,
    todos com o mesmo timestamp. É imutável e utiliza tuple para evitar alterações
    acidentais na coleção de valores.
    
    Atributos:
        station_id: Identificador da estação (maior que zero) de onde a leitura foi tomada.
        timestamp: Data e hora da leitura (timezone-aware).
        values: Tupla imutável de valores de leitura (não pode estar vazia).
    """

    station_id: int
    timestamp: datetime
    values: tuple[ReadingValue, ...]

    def __post_init__(self) -> None:
        """Valida os invariantes da leitura após inicialização."""
        if self.station_id <= 0:
            raise ValueError(
                "O identificador da estação deve ser maior que zero."
            )
        if self.timestamp.tzinfo is None:
            raise ValueError(
                "O timestamp da leitura deve ser timezone-aware."
            )
        if not self.values:
            raise ValueError(
                "Uma leitura deve conter pelo menos um valor."
            )
