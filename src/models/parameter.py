"""Modelo de domínio para Parâmetros Ambientais."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Parameter:
    """Representa um parâmetro ambiental monitorado.
    
    Parâmetro é uma grandeza mensurável (temperatura, pressão, umidade, etc.)
    que pode ser lido em uma estação ambiental.
    
    Atributos:
        id: Identificador único no banco de dados (None até persistência).
        code: Código único do parâmetro.
        name: Nome descritivo do parâmetro (ex: Temperature).
        unit: Unidade de medida (ex: °C) ou None se não aplicável.
    """

    id: int | None
    code: str
    name: str
    unit: str | None

    def __post_init__(self) -> None:
        """Valida os invariantes do parâmetro após inicialização."""
        if not self.code or not self.code.strip():
            raise ValueError(
                "O código do parâmetro não pode estar vazio."
            )
        if not self.name or not self.name.strip():
            raise ValueError(
                "O nome do parâmetro não pode estar vazio."
            )
