"""Modelo de domínio para Parâmetros Ambientais."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Parameter:
    """Representa um parâmetro ambiental monitorado.
    
    Parâmetro é uma grandeza mensurável (temperatura, pressão, umidade, etc.)
    que pode ser lido em uma estação ambiental.
    
    Mantém mapeamento entre:
    - Code: Identificador único interno (ex: AIR_TEMPERATURE)
    - CodeApi: Identificador recebido da API (ex: temperature)
    - CategoryId: Categoria do parâmetro (WEATHER, WATER, etc)
    
    Atributos:
        id: Identificador único no banco de dados (None até persistência).
        code: Código único interno do parâmetro.
        code_api: Código recebido da API (pode se repetir entre categorias).
        name: Nome descritivo do parâmetro.
        unit: Unidade de medida (ex: °C) ou None se não aplicável.
        category_id: ID da categoria do parâmetro (WEATHER, WATER, etc).
    """

    id: int | None
    code: str
    code_api: str
    name: str
    unit: str | None
    category_id: int

    def __post_init__(self) -> None:
        """Valida os invariantes do parâmetro após inicialização."""
        if not self.code or not self.code.strip():
            raise ValueError(
                "O código do parâmetro não pode estar vazio."
            )
        if not self.code_api or not self.code_api.strip():
            raise ValueError(
                "O código da API não pode estar vazio."
            )
        if not self.name or not self.name.strip():
            raise ValueError(
                "O nome do parâmetro não pode estar vazio."
            )
