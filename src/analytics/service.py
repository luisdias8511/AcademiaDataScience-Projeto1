"""Serviço de análise estatística de leituras ambientais."""

from collections import defaultdict

from src.models.reading import Reading
from src.models.statistics_result import StatisticsResult
from src.database.reading_repository import ReadingRepository

from .statistics import calcular_estatisticas


class AnalyticsService:
    """Calcula estatísticas por parâmetro para uma única estação."""

    def __init__(self, repository: ReadingRepository | None = None) -> None:
        """Inicializa o serviço com repositório opcional para buscar nomes de parâmetros.
        
        Args:
            repository: Repositório de leitura (opcional). Se não fornecido,
                       apenas código será usado.
        """
        self.repository = repository

    def calculate(
        self, readings: list[Reading]
    ) -> list[StatisticsResult]:
        """Analisa os valores de cada parâmetro no período recebido."""
        if not readings:
            return []

        station_ids = {reading.station_id for reading in readings}

        if len(station_ids) > 1:
            raise ValueError(
                "A análise deve receber leituras de uma única estação."
            )

        values_by_parameter = defaultdict(list)

        for reading in readings:
            for reading_value in reading.values:
                values_by_parameter[reading_value.parameter_code].append(
                    float(reading_value.value)
                )

        results = []

        for parameter_code, values in values_by_parameter.items():
            if len(values) < 2:
                raise ValueError(
                    f"O parâmetro '{parameter_code}' precisa de "
                    "pelo menos duas observações."
                )

            calculated = calcular_estatisticas(values)

            # Tentar buscar o nome do parâmetro
            parameter_name = None
            if self.repository:
                parameter = self.repository.get_parameter_by_code(parameter_code)
                if parameter:
                    parameter_name = parameter.name

            result = StatisticsResult(
                parameter_code=parameter_code,
                parameter_name=parameter_name,
                count=len(values),
                average=calculated["media"],
                median=calculated["mediana"],
                standard_deviation=calculated["desvio_padrao"],
                q1=calculated["q1"],
                q3=calculated["q3"],
                iqr=calculated["iqr"],
                lower_bound=calculated["limite_inferior"],
                upper_bound=calculated["limite_superior"],
                outliers=tuple(calculated["outliers"]),
            )

            results.append(result)

        return results