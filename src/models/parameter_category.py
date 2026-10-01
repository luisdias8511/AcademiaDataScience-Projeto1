"""Modelo de domínio para Categorias de Parâmetros."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ParameterCategory:
    """Representa uma categoria de parâmetros monitorados.
    
    Categoriza os parâmetros em domínios específicos:
    - WEATHER: Parâmetros meteorológicos
    - WATER: Parâmetros de qualidade da água
    
    Atributos:
        id: Identificador único no banco de dados (None até persistência).
        code: Código único da categoria (ex: WEATHER, WATER).
        name: Nome descritivo da categoria (ex: Parâmetros Meteorológicos).
    """

    id: int | None
    code: str
    name: str

    def __post_init__(self) -> None:
        """Valida os invariantes da categoria após inicialização."""
        if not self.code or not self.code.strip():
            raise ValueError(
                "O código da categoria não pode estar vazio."
            )
        if not self.name or not self.name.strip():
            raise ValueError(
                "O nome da categoria não pode estar vazio."
            )
