"""Modelo de domínio para Resultados de Análises Estatísticas."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class StatisticsResult:
    """Representa o resultado de uma análise estatística de um parâmetro.
    
    Contém medidas de tendência central, dispersão e identificação de outliers
    calculadas sobre os valores de um parâmetro específico em um período.
    
    Atributos:
        parameter_code: Código do parâmetro
        count: Quantidade de observações utilizadas no cálculo.
        average: Valor médio (mean) das observações.
        median: Valor da mediana (50º percentil).
        standard_deviation: Desvio padrão das observações.
        q1: Primeiro quartil (25º percentil).
        q3: Terceiro quartil (75º percentil).
        iqr: Intervalo interquartil (q3 - q1).
        lower_bound: Limite inferior para identificação de outliers (q1 - 1.5 * iqr).
        upper_bound: Limite superior para identificação de outliers (q3 + 1.5 * iqr).
        outliers: Tupla imutável com os valores identificados como outliers.
    """

    parameter_code: str
    count: int
    average: float
    median: float
    standard_deviation: float
    q1: float
    q3: float
    iqr: float
    lower_bound: float
    upper_bound: float
    outliers: tuple[float, ...]
    parameter_name: str | None = None

    def __post_init__(self) -> None:
        """Valida os invariantes do resultado estatístico após inicialização."""
        if not self.parameter_code or not self.parameter_code.strip():
            raise ValueError(
                "O código do parâmetro não pode estar vazio."
            )
        if self.count <= 0:
            raise ValueError(
                "A contagem de observações deve ser maior que zero."
            )
        if self.standard_deviation < 0:
            raise ValueError(
                "O desvio padrão não pode ser negativo."
            )
        if self.iqr < 0:
            raise ValueError(
                "O intervalo interquartil não pode ser negativo."
            )
