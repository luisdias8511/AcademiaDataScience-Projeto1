"""Modelo de domínio para Valores de Leitura."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class ReadingValue:
    """Representa um valor ambiental associado a uma leitura.
    
    ReadingValue é a materialização de uma medição de um parâmetro específico
    em um determinado momento e local (representado por Reading).
    
    O mapeamento para a tabela ReadingValues ocorre somente na camada
    de persistência. Durante ingestão e processamento, este objeto é
    independente de identificadores de banco de dados.
    
    Atributos:
        parameter_code: Código do parâmetro.
        value: Valor numérico da medição convertido para Decimal.
    """

    parameter_code: str
    value: Decimal
    unit: str | None

    def __post_init__(self) -> None:
        """Valida os invariantes do valor de leitura após inicialização."""
        if not self.parameter_code or not self.parameter_code.strip():
            raise ValueError(
                "O código do parâmetro não pode estar vazio."
            )
