"""Testes para exportação e geração de relatórios."""

import pytest
import csv
from pathlib import Path
from datetime import datetime, timezone
import tempfile

from src.reporting.csv_export import (
    export_statistics_to_csv,
    export_statistics_with_outliers_detail,
)
from src.models.statistics_result import StatisticsResult


class TestCSVExport:
    """Testes para exportação de estatísticas em CSV."""

    @pytest.fixture
    def sample_statistics(self):
        """Cria estatísticas de exemplo para exportação."""
        return [
            StatisticsResult(
                parameter_code="TEMPERATURE",
                count=10,
                average=22.5,
                median=22.0,
                standard_deviation=2.5,
                q1=20.0,
                q3=25.0,
                iqr=5.0,
                lower_bound=12.5,
                upper_bound=32.5,
                outliers=(10.0, 35.0),
            ),
            StatisticsResult(
                parameter_code="HUMIDITY",
                count=10,
                average=65.0,
                median=64.5,
                standard_deviation=5.0,
                q1=60.0,
                q3=70.0,
                iqr=10.0,
                lower_bound=45.0,
                upper_bound=85.0,
                outliers=(),
            ),
        ]

    def test_export_to_csv_creates_file(self, sample_statistics):
        """Deve criar arquivo CSV na pasta results."""
        csv_path = export_statistics_to_csv(sample_statistics, "weather")
        assert Path(csv_path).exists()
        assert csv_path.endswith(".csv")

    def test_export_to_csv_content(self, sample_statistics):
        """Deve exportar conteúdo correto no CSV."""
        csv_path = export_statistics_to_csv(sample_statistics, "weather")
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        assert len(rows) == 2  # Duas estatísticas
        assert rows[0]["parameter_code"] == "TEMPERATURE"
        assert float(rows[0]["average"]) == 22.5
        assert float(rows[0]["median"]) == 22.0

    def test_export_to_csv_headers(self, sample_statistics):
        """Deve incluir todos os cabeçalhos esperados."""
        csv_path = export_statistics_to_csv(sample_statistics, "weather")
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
        
        expected_headers = [
            "parameter_code", "count", "average", "median", "standard_deviation",
            "q1", "q3", "iqr", "lower_bound", "upper_bound", "outliers_count", "outliers"
        ]
        assert headers == expected_headers

    def test_export_to_csv_numeric_precision(self, sample_statistics):
        """Deve exportar números com 2 casas decimais."""
        csv_path = export_statistics_to_csv(sample_statistics, "weather")
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        # Verificar formato decimal
        average_str = rows[0]["average"]
        assert "." in average_str
        decimal_places = len(average_str.split(".")[1])
        assert decimal_places == 2

    def test_export_to_csv_file_location(self, sample_statistics):
        """Deve exportar para pasta results."""
        csv_path = export_statistics_to_csv(sample_statistics, "weather")
        assert "results" in csv_path

    def test_export_to_csv_filename_contains_category(self, sample_statistics):
        """Nome do arquivo deve conter categoria (weather/water)."""
        csv_path_weather = export_statistics_to_csv(sample_statistics, "weather")
        csv_path_water = export_statistics_to_csv(sample_statistics, "water")
        
        assert "weather" in csv_path_weather
        assert "water" in csv_path_water
        assert csv_path_weather != csv_path_water

    def test_export_to_csv_timestamp_in_filename(self, sample_statistics):
        """Arquivo deve conter timestamp para unicidade."""
        csv_path = export_statistics_to_csv(sample_statistics, "weather")
        # Formato esperado: weather_YYYYMMDD_HHMMSS.csv
        assert ".csv" in csv_path
        filename = Path(csv_path).name
        # Deve conter dígitos (timestamp)
        assert any(c.isdigit() for c in filename)

    def test_export_empty_statistics(self):
        """Deve rejeitar tentativa de exportar CSV com lista vazia."""
        with pytest.raises(ValueError):
            csv_path = export_statistics_to_csv([], "weather")


class TestOutliersDetailExport:
    """Testes para exportação de outliers com detalhes."""

    @pytest.fixture
    def sample_statistics_with_outliers(self):
        """Cria estatísticas com outliers para testes."""
        return [
            StatisticsResult(
                parameter_code="TEMPERATURE",
                count=10,
                average=22.5,
                median=22.0,
                standard_deviation=2.5,
                q1=20.0,
                q3=25.0,
                iqr=5.0,
                lower_bound=12.5,
                upper_bound=32.5,
                outliers=(10.0, 35.0, 8.5),
            ),
        ]

    def test_export_outliers_creates_file(self, sample_statistics_with_outliers):
        """Deve criar arquivo CSV de outliers."""
        csv_path = export_statistics_with_outliers_detail(
            sample_statistics_with_outliers, "weather"
        )
        assert Path(csv_path).exists()
        assert "outliers" in csv_path.lower()

    def test_export_outliers_content(self, sample_statistics_with_outliers):
        """Deve listar cada outlier em linha separada."""
        csv_path = export_statistics_with_outliers_detail(
            sample_statistics_with_outliers, "weather"
        )
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        # Deve ter 3 linhas, uma para cada outlier
        assert len(rows) == 3

    def test_export_outliers_no_outliers(self):
        """Deve exportar arquivo vazio quando sem outliers."""
        statistics = [
            StatisticsResult(
                parameter_code="TEMPERATURE",
                count=10,
                average=22.5,
                median=22.0,
                standard_deviation=2.5,
                q1=20.0,
                q3=25.0,
                iqr=5.0,
                lower_bound=12.5,
                upper_bound=32.5,
                outliers=(),  # Sem outliers
            ),
        ]
        csv_path = export_statistics_with_outliers_detail(statistics, "weather")
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        assert len(rows) == 0

    def test_export_outliers_headers(self, sample_statistics_with_outliers):
        """Deve conter cabeçalhos apropriados."""
        csv_path = export_statistics_with_outliers_detail(
            sample_statistics_with_outliers, "weather"
        )
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
        
        assert "parameter_code" in headers
        assert "outlier_value" in headers or "outliers" in headers

    def test_export_outliers_multiple_parameters(self):
        """Deve exportar outliers de múltiplos parâmetros."""
        statistics = [
            StatisticsResult(
                parameter_code="TEMPERATURE",
                count=10,
                average=22.5,
                median=22.0,
                standard_deviation=2.5,
                q1=20.0,
                q3=25.0,
                iqr=5.0,
                lower_bound=12.5,
                upper_bound=32.5,
                outliers=(10.0, 35.0),
            ),
            StatisticsResult(
                parameter_code="HUMIDITY",
                count=10,
                average=65.0,
                median=64.5,
                standard_deviation=5.0,
                q1=60.0,
                q3=70.0,
                iqr=10.0,
                lower_bound=45.0,
                upper_bound=85.0,
                outliers=(90.0, 40.0),
            ),
        ]
        csv_path = export_statistics_with_outliers_detail(statistics, "weather")
        
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        # Deve ter 4 linhas: 2 do TEMPERATURE + 2 do HUMIDITY
        assert len(rows) == 4
        
        # Verificar parâmetros
        parameters = [row["parameter_code"] for row in rows]
        assert parameters.count("TEMPERATURE") == 2
        assert parameters.count("HUMIDITY") == 2

    def test_export_outliers_file_location(self, sample_statistics_with_outliers):
        """Deve exportar para pasta results."""
        csv_path = export_statistics_with_outliers_detail(
            sample_statistics_with_outliers, "weather"
        )
        assert "results" in csv_path

    def test_export_outliers_different_categories(self, sample_statistics_with_outliers):
        """Nomes diferentes para weather e water."""
        path_weather = export_statistics_with_outliers_detail(
            sample_statistics_with_outliers, "weather"
        )
        path_water = export_statistics_with_outliers_detail(
            sample_statistics_with_outliers, "water"
        )
        
        assert "weather" in path_weather
        assert "water" in path_water
        assert path_weather != path_water
