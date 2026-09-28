"""Modelo de domínio para Estações Ambientais."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class Station:
    """Representa uma estação ambiental cadastrada pelo sistema.
    
    A estação é a entidade central que agrupa leituras de dados ambientais.
    Deve ser cadastrada manualmente no banco de dados antes de ser utilizada.
    
    Atributos:
        id: Identificador único e maior que zero.
        code: Código único da estação (não pode estar vazio).
        name: Nome descritivo da estação (não pode estar vazio).
        latitude: Coordenada de latitude, entre -90 e 90 graus.
        longitude: Coordenada de longitude, entre -180 e 180 graus.
    """

    id: int
    code: str
    name: str
    latitude: Decimal
    longitude: Decimal

    def __post_init__(self) -> None:
        """Valida os invariantes da estação após inicialização."""
        if self.id <= 0:
            raise ValueError(
                "O identificador da estação deve ser maior que zero."
            )
        if not self.code or not self.code.strip():
            raise ValueError(
                "O código da estação não pode estar vazio."
            )
        if not self.name or not self.name.strip():
            raise ValueError(
                "O nome da estação não pode estar vazio."
            )
        if not (-90 <= self.latitude <= 90):
            raise ValueError(
                "A latitude deve estar entre -90 e 90 graus."
            )
        if not (-180 <= self.longitude <= 180):
            raise ValueError(
                "A longitude deve estar entre -180 e 180 graus."
            )
