"""Serviço de analytics mock para demonstração."""

from src.models.reading import Reading
from src.models.statistics_result import StatisticsResult


class MockAnalyticsService:
    """Simula um serviço de análise estatística sem usar pandas/numpy."""

    def calculate(self, readings: list[Reading]) -> list[StatisticsResult]:
        """Retorna estatísticas fixas para demonstração.
        
        Args:
            readings: Lista de leituras (não é realmente utilizada)
            
        Returns:
            Lista com estatísticas para cada parâmetro
        """
        results = [
            StatisticsResult(
                parameter_code="temperature",
                count=10,
                average=21.50,
                median=21.00,
                standard_deviation=1.20,
                q1=20.00,
                q3=22.00,
                iqr=2.00,
                lower_bound=17.00,
                upper_bound=25.00,
                outliers=(),
            ),
            StatisticsResult(
                parameter_code="humidity",
                count=10,
                average=65.00,
                median=64.00,
                standard_deviation=3.50,
                q1=62.00,
                q3=68.00,
                iqr=6.00,
                lower_bound=53.00,
                upper_bound=77.00,
                outliers=(),
            ),
            StatisticsResult(
                parameter_code="pressure",
                count=10,
                average=1013.25,
                median=1012.90,
                standard_deviation=2.00,
                q1=1011.50,
                q3=1014.00,
                iqr=2.50,
                lower_bound=1007.75,
                upper_bound=1017.75,
                outliers=(),
            ),
            StatisticsResult(
                parameter_code="wind_speed",
                count=10,
                average=12.40,
                median=12.10,
                standard_deviation=1.10,
                q1=11.50,
                q3=13.00,
                iqr=1.50,
                lower_bound=9.25,
                upper_bound=15.25,
                outliers=(),
            ),
        ]
        return results
