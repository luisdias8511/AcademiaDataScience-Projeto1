"""Testes de integração do pipeline completo."""

import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch, MagicMock

from src.models.reading import Reading
from src.models.reading_value import ReadingValue
from src.models.station import Station
from src.models.statistics_result import StatisticsResult
from src.processing.reading_processor import ReadingProcessor
from src.analytics.service import AnalyticsService
from src.reporting.csv_export import export_statistics_to_csv
from decimal import Decimal


class TestEndToEndPipeline:
    """Testes de integração do pipeline completo."""

    @pytest.fixture
    def complete_pipeline(self):
        """Componentes necessários para o pipeline."""
        return {
            "processor": ReadingProcessor(),
            "analytics": AnalyticsService(),
        }

    @pytest.fixture
    def realistic_readings(self):
        """Cria dados realistas para teste de integração."""
        base_time = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        readings = []
        
        # Simular 20 dias de leituras meteorológicas
        for day in range(20):
            timestamp = base_time + timedelta(days=day)
            # Simular variação natural de temperatura (20-30°C)
            temp = 25.0 + (day % 5) - 2  # Varia de 23 a 27
            humidity = 60.0 + (day % 3) * 5  # Varia de 60 a 70
            
            values = (
                ReadingValue(parameter_code="TEMPERATURE", value=str(temp)),
                ReadingValue(parameter_code="HUMIDITY", value=str(humidity)),
            )
            readings.append(
                Reading(
                    station_id=1,
                    timestamp=timestamp,
                    values=values,
                )
            )
        
        return readings

    def test_pipeline_validate_analyze_export(self, complete_pipeline, realistic_readings):
        """Testa fluxo completo: validar → analisar → exportar."""
        processor = complete_pipeline["processor"]
        analytics = complete_pipeline["analytics"]
        
        # 1. Validar cada leitura
        for reading in realistic_readings:
            processor.validate(reading)  # Não deve lançar exceção
        
        # 2. Analisar estatísticas
        results = analytics.calculate(realistic_readings)
        assert len(results) > 0
        
        # 3. Verificar que os resultados contêm outliers
        assert all(isinstance(r, StatisticsResult) for r in results)
        for result in results:
            assert result.count >= 2
            assert result.iqr >= 0

    def test_pipeline_with_outliers(self, complete_pipeline):
        """Testa pipeline com detecção de outliers."""
        processor = complete_pipeline["processor"]
        analytics = complete_pipeline["analytics"]
        
        # Criar dados com outliers óbvios
        base_time = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        readings = []
        
        for i in range(15):
            timestamp = base_time + timedelta(days=i)
            # Valores normais: 20-22
            temp = 21.0 + (i % 2) * 0.5
            
            values = (ReadingValue(parameter_code="TEMPERATURE", value=str(temp)),)
            readings.append(Reading(station_id=1, timestamp=timestamp, values=values))
        
        # Adicionar outliers
        readings.append(
            Reading(
                station_id=1,
                timestamp=base_time + timedelta(days=15),
                values=(ReadingValue(parameter_code="TEMPERATURE", value="50.0"),),
            )
        )
        
        # Validar e analisar
        for reading in readings:
            processor.validate(reading)
        
        results = analytics.calculate(readings)
        
        # Verificar que outliers foram detectados
        assert len(results) == 1
        assert len(results[0].outliers) > 0
        assert 50.0 in results[0].outliers

    def test_pipeline_empty_data_handling(self, complete_pipeline):
        """Testa pipeline com dados vazios."""
        analytics = complete_pipeline["analytics"]
        
        # Analytics deve retornar lista vazia
        results = analytics.calculate([])
        assert results == []

    def test_pipeline_single_parameter(self, complete_pipeline):
        """Testa pipeline com apenas um parâmetro."""
        processor = complete_pipeline["processor"]
        analytics = complete_pipeline["analytics"]
        
        base_time = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        readings = []
        
        for i in range(10):
            readings.append(
                Reading(
                    station_id=1,
                    timestamp=base_time + timedelta(days=i),
                    values=(ReadingValue(parameter_code="TEMPERATURE", value=str(20 + i)),),
                )
            )
        
        for reading in readings:
            processor.validate(reading)
        
        results = analytics.calculate(readings)
        assert len(results) == 1
        assert results[0].parameter_code == "TEMPERATURE"
        assert results[0].count == 10

    def test_pipeline_multiple_parameters(self, complete_pipeline, realistic_readings):
        """Testa pipeline com múltiplos parâmetros."""
        analytics = complete_pipeline["analytics"]
        
        results = analytics.calculate(realistic_readings)
        
        # Deve ter resultados para TEMPERATURE e HUMIDITY
        assert len(results) == 2
        parameter_codes = {r.parameter_code for r in results}
        assert "TEMPERATURE" in parameter_codes
        assert "HUMIDITY" in parameter_codes

    def test_pipeline_statistics_consistency(self, complete_pipeline, realistic_readings):
        """Testa que estatísticas são consistentes."""
        analytics = complete_pipeline["analytics"]
        
        results = analytics.calculate(realistic_readings)
        
        for result in results:
            # Q1 <= Mediana <= Q3
            assert result.q1 <= result.median <= result.q3
            # IQR = Q3 - Q1
            assert abs(result.iqr - (result.q3 - result.q1)) < 0.01
            # Limites de outliers
            expected_lower = result.q1 - 1.5 * result.iqr
            expected_upper = result.q3 + 1.5 * result.iqr
            assert abs(result.lower_bound - expected_lower) < 0.01
            assert abs(result.upper_bound - expected_upper) < 0.01

    def test_pipeline_export_after_analysis(self, complete_pipeline, realistic_readings):
        """Testa exportação após análise."""
        analytics = complete_pipeline["analytics"]
        
        results = analytics.calculate(realistic_readings)
        
        # Exportar para CSV
        csv_path = export_statistics_to_csv(results, "weather")
        
        # Verificar arquivo foi criado
        from pathlib import Path
        assert Path(csv_path).exists()
        assert "weather" in csv_path

    def test_pipeline_large_dataset(self, complete_pipeline):
        """Testa pipeline com conjunto grande de dados."""
        processor = complete_pipeline["processor"]
        analytics = complete_pipeline["analytics"]
        
        # Criar 365 dias de dados
        base_time = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        readings = []
        
        for day in range(365):
            timestamp = base_time + timedelta(days=day)
            # Simular variação sazonal (inverno/verão)
            temp = 20.0 + 10 * (day % 182 / 182)  # Varia de 20 a 30
            
            readings.append(
                Reading(
                    station_id=1,
                    timestamp=timestamp,
                    values=(ReadingValue(parameter_code="TEMPERATURE", value=str(temp)),),
                )
            )
        
        # Processar e analisar
        for reading in readings:
            processor.validate(reading)
        
        results = analytics.calculate(readings)
        
        assert len(results) == 1
        assert results[0].count == 365

    def test_pipeline_error_handling(self, complete_pipeline):
        """Testa tratamento de erros no pipeline."""
        analytics = complete_pipeline["analytics"]
        
        # Criar leituras de estações diferentes
        readings = [
            Reading(
                station_id=1,
                timestamp=datetime.now(timezone.utc),
                values=(ReadingValue(parameter_code="TEMP", value="25"),),
            ),
            Reading(
                station_id=2,  # Estação diferente
                timestamp=datetime.now(timezone.utc),
                values=(ReadingValue(parameter_code="TEMP", value="26"),),
            ),
        ]
        
        # Analytics deve rejeitar
        with pytest.raises(ValueError):
            analytics.calculate(readings)

    def test_pipeline_reproducibility(self, complete_pipeline, realistic_readings):
        """Testa que resultados são reproducíveis."""
        analytics = complete_pipeline["analytics"]
        
        # Executar análise duas vezes
        results1 = analytics.calculate(realistic_readings)
        results2 = analytics.calculate(realistic_readings)
        
        # Resultados devem ser idênticos
        assert len(results1) == len(results2)
        for r1, r2 in zip(results1, results2):
            assert r1.parameter_code == r2.parameter_code
            assert r1.average == r2.average
            assert r1.median == r2.median
            assert r1.standard_deviation == r2.standard_deviation


class TestReadingStreamProcessing:
    """Testes para processamento de fluxo de leituras."""

    def test_stream_processing_with_validation(self):
        """Testa processamento sequencial com validação."""
        processor = ReadingProcessor()
        base_time = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        
        readings_to_process = []
        
        # Criar stream de leituras
        for i in range(10):
            reading = Reading(
                station_id=1,
                timestamp=base_time + timedelta(hours=i),
                values=(ReadingValue(parameter_code="TEMPERATURE", value=str(20 + i)),),
            )
            
            # Validar antes de adicionar
            processor.validate(reading)
            readings_to_process.append(reading)
        
        # Verificar que todos foram adicionados
        assert len(readings_to_process) == 10

    def test_filtering_invalid_readings(self):
        """Testa filtragem de leituras inválidas."""
        processor = ReadingProcessor()
        base_time = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        
        readings = []
        invalid_count = 0
        
        for i in range(10):
            try:
                reading = Reading(
                    station_id=1 if i < 8 else 0,  # Últimas 2 com ID inválido
                    timestamp=base_time + timedelta(hours=i),
                    values=(ReadingValue(parameter_code="TEMPERATURE", value=str(20 + i)),),
                )
                processor.validate(reading)
                readings.append(reading)
            except ValueError:
                invalid_count += 1
        
        assert len(readings) == 8
        assert invalid_count == 2
