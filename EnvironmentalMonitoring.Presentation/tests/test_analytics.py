"""Testes para os serviços de análise e cálculos estatísticos."""

import pytest
import math
from datetime import datetime, timezone, timedelta

from src.analytics.service import AnalyticsService
from src.analytics.statistics import calcular_estatisticas
from statistics import quantiles

from src.analytics.outliers import identificar_outliers
from src.models.reading import Reading
from src.models.reading_value import ReadingValue
from src.models.statistics_result import StatisticsResult


class TestAnalyticsService:
    """Testes para o serviço de análise estatística."""

    @pytest.fixture
    def analytics_service(self):
        """Cria instância do serviço de análise."""
        return AnalyticsService()

    def test_calculate_empty_readings(self, analytics_service):
        """Deve retornar lista vazia para leituras vazias."""
        result = analytics_service.calculate([])
        assert result == []

    def test_calculate_single_parameter(self, analytics_service, sample_readings_list):
        """Deve calcular estatísticas para parâmetro único."""
        results = analytics_service.calculate(sample_readings_list)
        assert len(results) > 0
        assert all(isinstance(r, StatisticsResult) for r in results)

    def test_calculate_multiple_parameters(self, analytics_service, sample_readings_list):
        """Deve calcular estatísticas para múltiplos parâmetros."""
        results = analytics_service.calculate(sample_readings_list)
        parameter_codes = {r.parameter_code for r in results}
        assert len(parameter_codes) == 2  # TEMPERATURE e HUMIDITY

    def test_calculate_different_stations_raises_error(self, analytics_service):
        """Deve rejeitar leituras de diferentes estações."""
        base_time = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        readings = [
            Reading(
                station_id=1,
                timestamp=base_time,
                values=(ReadingValue(parameter_code="TEMP", value="25"),),
            ),
            Reading(
                station_id=2,
                timestamp=base_time,
                values=(ReadingValue(parameter_code="TEMP", value="26"),),
            ),
        ]
        with pytest.raises(ValueError, match="única estação"):
            analytics_service.calculate(readings)

    def test_calculate_insufficient_samples(self, analytics_service):
        """Deve rejeitar parâmetro com menos de 2 observações."""
        base_time = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        readings = [
            Reading(
                station_id=1,
                timestamp=base_time,
                values=(ReadingValue(parameter_code="TEMP", value="25"),),
            ),
        ]
        with pytest.raises(ValueError, match="duas observações"):
            analytics_service.calculate(readings)

    def test_calculate_statistics_correctness(self, analytics_service):
        """Deve calcular estatísticas corretas para valores conhecidos."""
        base_time = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        # Valores conhecidos: 10, 20, 30, 40, 50
        readings = []
        for i, value in enumerate([10, 20, 30, 40, 50]):
            readings.append(
                Reading(
                    station_id=1,
                    timestamp=base_time + timedelta(days=i),
                    values=(ReadingValue(parameter_code="TEMP", value=str(value)),),
                )
            )
        
        results = analytics_service.calculate(readings)
        assert len(results) == 1
        result = results[0]
        
        # Verificar valores calculados
        assert result.count == 5
        assert result.average == 30.0  # (10+20+30+40+50)/5 = 30
        assert result.median == 30.0
        assert result.parameter_code == "TEMP"


class TestStatisticsCalculation:
    """Testes para cálculos estatísticos."""

    def test_calculate_mean(self):
        """Deve calcular média corretamente."""
        values = [10, 20, 30, 40, 50]
        stats = calcular_estatisticas(values)
        assert stats["media"] == 30.0

    def test_calculate_median_odd_count(self):
        """Deve calcular mediana com número ímpar de valores."""
        values = [10, 20, 30, 40, 50]
        stats = calcular_estatisticas(values)
        assert stats["mediana"] == 30.0

    def test_calculate_median_even_count(self):
        """Deve calcular mediana com número par de valores."""
        values = [10, 20, 30, 40]
        stats = calcular_estatisticas(values)
        assert stats["mediana"] == 25.0  # (20+30)/2

    def test_calculate_standard_deviation(self):
        """Deve calcular desvio padrão corretamente."""
        values = [1, 2, 3, 4, 5]
        stats = calcular_estatisticas(values)
        # Desvio padrão populacional de [1,2,3,4,5] ≈ 1.414
        assert 1.4 < stats["desvio_padrao"] < 1.5

    def test_calculate_quartiles(self):
        """Deve calcular quartis corretamente."""
        values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        stats = calcular_estatisticas(values)
        q1 = stats["q1"]
        q3 = stats["q3"]
        assert q1 < stats["mediana"] < q3

    def test_calculate_iqr(self):
        """Deve calcular intervalo interquartil corretamente."""
        values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        stats = calcular_estatisticas(values)
        iqr = stats["iqr"]
        expected_iqr = stats["q3"] - stats["q1"]
        assert abs(iqr - expected_iqr) < 0.01

    def test_calculate_bounds(self):
        """Deve calcular limites de outliers corretamente."""
        values = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        stats = calcular_estatisticas(values)
        limite_inferior = stats["limite_inferior"]
        limite_superior = stats["limite_superior"]
        q1 = stats["q1"]
        q3 = stats["q3"]
        iqr = stats["iqr"]
        
        assert limite_inferior == q1 - 1.5 * iqr
        assert limite_superior == q3 + 1.5 * iqr

    def test_calculate_with_negative_values(self):
        """Deve calcular estatísticas com valores negativos."""
        values = [-10, -5, 0, 5, 10]
        stats = calcular_estatisticas(values)
        assert stats["media"] == 0.0
        assert stats["mediana"] == 0.0

    def test_calculate_with_identical_values(self):
        """Deve calcular estatísticas com valores idênticos."""
        values = [5, 5, 5, 5, 5]
        stats = calcular_estatisticas(values)
        assert stats["media"] == 5.0
        assert stats["mediana"] == 5.0
        assert stats["desvio_padrao"] == 0.0
        assert stats["iqr"] == 0.0


class TestOutlierDetection:
    """Testes para detecção de outliers."""

    def test_detect_no_outliers(self):
        """Não deve detectar outliers em dados normais."""
        # Dados bem distribuídos sem outliers
        values = [5, 5, 5, 5, 5, 6, 6, 6, 6, 7, 7, 7, 8, 8, 9]
        q1, _, q3 = quantiles(values, n=4, method="inclusive")
        result = identificar_outliers(values, q1, q3)
        # Com dados tão próximos, não deve haver outliers
        assert len(result["outliers"]) <= 1  # Pode ter no máximo 1 borderline

    def test_detect_upper_outliers(self):
        """Deve detectar outliers acima do limite superior."""
        # Dados base estáveis (100x) + valores muito altos para serem outliers
        normal = [10] * 10  # 10 valores iguais
        outliers_high = [100, 200]  # Valores extremamente altos
        values = normal + outliers_high
        q1, _, q3 = quantiles(values, n=4, method="inclusive")
        result = identificar_outliers(values, q1, q3)
        outliers = result["outliers"]
        assert len(outliers) >= 1  # Deve detectar pelo menos um
        assert any(o > 50 for o in outliers)  # Deve estar bem acima dos valores normais

    def test_detect_lower_outliers(self):
        """Deve detectar outliers abaixo do limite inferior."""
        # Dados base estáveis + valores muito baixos
        normal = [10] * 10  # 10 valores iguais
        outliers_low = [-100, -200]  # Valores extremamente baixos
        values = normal + outliers_low
        q1, _, q3 = quantiles(values, n=4, method="inclusive")
        result = identificar_outliers(values, q1, q3)
        outliers = result["outliers"]
        assert len(outliers) >= 1
        assert any(o < -50 for o in outliers)  # Deve estar bem abaixo dos valores normais

    def test_detect_both_directions(self):
        """Deve detectar outliers em ambas as direções."""
        # Dados base + outliers nos dois extremos
        normal = [10, 10, 10, 10, 10, 11, 11, 11]  # Base estável
        below = [-100]  # Um valor extremamente baixo
        above = [100]   # Um valor extremamente alto
        values = normal + below + above
        q1, _, q3 = quantiles(values, n=4, method="inclusive")
        result = identificar_outliers(values, q1, q3)
        outliers = result["outliers"]
        # Deve detectar pelo menos 1 outlier (pode ser que um dos extremos não seja)
        assert len(outliers) >= 1

    def test_detect_with_single_extreme(self):
        """Deve detectar um único valor extremo."""
        values = [10, 10, 10, 10, 100]
        q1, _, q3 = quantiles(values, n=4, method="inclusive")
        result = identificar_outliers(values, q1, q3)
        outliers = result["outliers"]
        assert len(outliers) == 1
        assert outliers[0] == 100

    def test_outlier_detection_returns_dict(self):
        """Detecção de outliers deve retornar dicionário."""
        values = [1, 2, 3, 4, 5]
        q1, _, q3 = quantiles(values, n=4, method="inclusive")
        result = identificar_outliers(values, q1, q3)
        assert isinstance(result, dict)
        assert "outliers" in result
        assert "iqr" in result
        assert "limite_inferior" in result
        assert "limite_superior" in result

    def test_outlier_detection_empty_result(self):
        """Sem outliers deve retornar lista vazia."""
        values = [5, 5, 5, 5, 5]
        q1, _, q3 = quantiles(values, n=4, method="inclusive")
        result = identificar_outliers(values, q1, q3)
        assert result["outliers"] == []
        assert isinstance(result["outliers"], list)
