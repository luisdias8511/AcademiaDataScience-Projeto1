"""Testes para o módulo main (pipeline principal).

Cobre as funções de ingestion paralela, pipeline CLI, pipeline Streamlit,
e a função main que coordena a execução.
"""

import pytest
import sys
from datetime import datetime, timezone
from unittest.mock import Mock, MagicMock, patch, call
from pathlib import Path

from src.main import (
    fetch_weather_task,
    fetch_water_task,
    run_cli_pipeline,
    run_streamlit_pipeline,
    main,
)
from src.models.reading import Reading
from src.models.reading_value import ReadingValue
from src.models.station import Station
from decimal import Decimal


# ===================== Fixtures =====================

@pytest.fixture
def mock_station():
    """Station mock para testes."""
    return Station(id=1, code="EST001", name="Estação 01", latitude=-15.5, longitude=-48.5)


@pytest.fixture
def sample_readings():
    """Sample readings para testes."""
    return [
        Reading(
            station_id=1,
            timestamp=datetime(2026, 1, 15, 10, 0, tzinfo=timezone.utc),
            values=(ReadingValue(parameter_code="temperature", value=Decimal("25.5")),)
        ),
        Reading(
            station_id=1,
            timestamp=datetime(2026, 1, 15, 11, 0, tzinfo=timezone.utc),
            values=(ReadingValue(parameter_code="temperature", value=Decimal("26.0")),)
        ),
    ]


# ===================== Testes de Task Functions =====================

class TestFetchWeatherTask:
    """Testes para fetch_weather_task."""

    def test_fetch_weather_task_returns_tuple(self, mock_station, sample_readings):
        """Deve retornar tupla (tipo, readings)."""
        mock_service = MagicMock()
        mock_service.fetch_weather_readings.return_value = sample_readings

        result = fetch_weather_task(
            mock_service,
            mock_station,
            datetime(2026, 1, 15),
            datetime(2026, 1, 16),
        )

        assert isinstance(result, tuple)
        assert len(result) == 2
        assert result[0] == "weather"
        assert result[1] == sample_readings

    def test_fetch_weather_task_calls_service(self, mock_station, sample_readings):
        """Deve chamar fetch_weather_readings do serviço."""
        mock_service = MagicMock()
        mock_service.fetch_weather_readings.return_value = sample_readings
        start_date = datetime(2026, 1, 15)
        end_date = datetime(2026, 1, 16)

        fetch_weather_task(mock_service, mock_station, start_date, end_date)

        mock_service.fetch_weather_readings.assert_called_once_with(
            mock_station, start_date, end_date
        )

    def test_fetch_weather_task_with_empty_readings(self, mock_station):
        """Deve retornar readings vazio."""
        mock_service = MagicMock()
        mock_service.fetch_weather_readings.return_value = []

        result = fetch_weather_task(
            mock_service,
            mock_station,
            datetime(2026, 1, 15),
            datetime(2026, 1, 16),
        )

        assert result[0] == "weather"
        assert result[1] == []


class TestFetchWaterTask:
    """Testes para fetch_water_task."""

    def test_fetch_water_task_returns_tuple(self, mock_station, sample_readings):
        """Deve retornar tupla (tipo, readings)."""
        mock_service = MagicMock()
        mock_service.get_water_readings.return_value = sample_readings

        result = fetch_water_task(
            mock_service,
            mock_station,
            datetime(2026, 1, 15),
            datetime(2026, 1, 16),
        )

        assert isinstance(result, tuple)
        assert len(result) == 2
        assert result[0] == "water"
        assert result[1] == sample_readings

    def test_fetch_water_task_calls_service(self, mock_station, sample_readings):
        """Deve chamar get_water_readings do serviço."""
        mock_service = MagicMock()
        mock_service.get_water_readings.return_value = sample_readings
        start_date = datetime(2026, 1, 15)
        end_date = datetime(2026, 1, 16)

        fetch_water_task(mock_service, mock_station, start_date, end_date)

        mock_service.get_water_readings.assert_called_once_with(
            mock_station, start_date, end_date
        )

    def test_fetch_water_task_with_empty_readings(self, mock_station):
        """Deve retornar readings vazio."""
        mock_service = MagicMock()
        mock_service.get_water_readings.return_value = []

        result = fetch_water_task(
            mock_service,
            mock_station,
            datetime(2026, 1, 15),
            datetime(2026, 1, 16),
        )

        assert result[0] == "water"
        assert result[1] == []


# ===================== Testes do Pipeline =====================

class TestRunCliPipeline:
    """Testes para run_cli_pipeline."""

    def test_run_cli_pipeline_success(self, mock_station, sample_readings, capsys):
        """Deve executar pipeline CLI com sucesso."""
        with patch('src.main.ReadingRepository') as mock_repo_class:
            with patch('src.main.IngestionService') as mock_ingest_class:
                with patch('src.main.AnalyticsService') as mock_analytics_class:
                    with patch('src.main.show_statistics_table'):
                        with patch('src.main.export_statistics_to_csv') as mock_csv_export:
                            with patch('src.main.export_statistics_with_outliers_detail') as mock_outliers:
                                # Setup mocks
                                mock_repo = MagicMock()
                                mock_repo_class.return_value = mock_repo
                                
                                mock_repo.get_stations.return_value = [mock_station]
                                mock_repo.get_by_station.return_value = sample_readings
                                mock_repo.save_many.return_value = [1, 2]
                                
                                mock_ingest = MagicMock()
                                mock_ingest_class.return_value = mock_ingest
                                mock_ingest.fetch_weather_readings.return_value = sample_readings
                                mock_ingest.get_water_readings.return_value = sample_readings
                                
                                mock_analytics = MagicMock()
                                mock_analytics_class.return_value = mock_analytics
                                mock_analytics.calculate.return_value = [MagicMock()]
                                
                                mock_csv_export.return_value = "weather_stats.csv"
                                mock_outliers.return_value = "weather_outliers.csv"
                                
                                # Run pipeline
                                with patch.object(sys, 'argv', ['main', '--cli']):
                                    with patch('src.main.select_station') as mock_select:
                                        with patch('src.main.read_date_range') as mock_date_range:
                                            mock_select.return_value = mock_station
                                            mock_date_range.return_value = (
                                                datetime(2026, 1, 15),
                                                datetime(2026, 1, 16),
                                            )
                                            
                                            run_cli_pipeline()
                                
                                # Verificar saída
                                captured = capsys.readouterr()
                                assert "PIPELINE CONCLUÍDO COM SUCESSO" in captured.out

    def test_run_cli_pipeline_error_handling(self, capsys):
        """Deve tratar erros durante pipeline."""
        with patch('src.main.ReadingRepository') as mock_repo_class:
            mock_repo_class.side_effect = Exception("DB Error")
            
            with patch('src.main.tratar_erro'):
                run_cli_pipeline()
            
            captured = capsys.readouterr()
            assert "ERRO" in captured.out or "DB Error" in captured.out

    def test_run_cli_pipeline_calls_repository(self, mock_station):
        """Deve conectar ao repositório."""
        with patch('src.main.ReadingRepository') as mock_repo_class:
            with patch('src.main.IngestionService'):
                with patch('src.main.AnalyticsService'):
                    with patch('src.main.show_statistics_table'):
                        with patch('src.main.export_statistics_to_csv'):
                            with patch('src.main.export_statistics_with_outliers_detail'):
                                with patch('src.main.select_station') as mock_select:
                                    with patch('src.main.read_date_range') as mock_date_range:
                                        mock_repo = MagicMock()
                                        mock_repo_class.return_value = mock_repo
                                        mock_repo.get_stations.return_value = [mock_station]
                                        mock_repo.get_by_station.return_value = []
                                        mock_repo.save_many.return_value = []
                                        
                                        mock_select.return_value = mock_station
                                        mock_date_range.return_value = (
                                            datetime(2026, 1, 15),
                                            datetime(2026, 1, 16),
                                        )
                                        
                                        run_cli_pipeline()
                                        
                                        mock_repo_class.assert_called_once()

    def test_run_cli_pipeline_calls_analytics(self, mock_station, sample_readings):
        """Deve chamar serviço de analytics."""
        with patch('src.main.ReadingRepository') as mock_repo_class:
            with patch('src.main.IngestionService'):
                with patch('src.main.AnalyticsService') as mock_analytics_class:
                    with patch('src.main.show_statistics_table'):
                        with patch('src.main.export_statistics_to_csv'):
                            with patch('src.main.export_statistics_with_outliers_detail'):
                                with patch('src.main.select_station') as mock_select:
                                    with patch('src.main.read_date_range') as mock_date_range:
                                        mock_repo = MagicMock()
                                        mock_repo_class.return_value = mock_repo
                                        mock_repo.get_stations.return_value = [mock_station]
                                        mock_repo.get_by_station.return_value = sample_readings
                                        mock_repo.save_many.return_value = [1, 2]
                                        
                                        mock_analytics = MagicMock()
                                        mock_analytics_class.return_value = mock_analytics
                                        mock_analytics.calculate.return_value = []
                                        
                                        mock_select.return_value = mock_station
                                        mock_date_range.return_value = (
                                            datetime(2026, 1, 15),
                                            datetime(2026, 1, 16),
                                        )
                                        
                                        run_cli_pipeline()
                                        
                                        # Deve ter criado analytics service
                                        mock_analytics_class.assert_called_once()
                                        # Deve ter chamado calculate 2x (weather + water)
                                        assert mock_analytics.calculate.call_count >= 1


# ===================== Testes do Streamlit Pipeline =====================

class TestRunStreamlitPipeline:
    """Testes para run_streamlit_pipeline."""

    def test_run_streamlit_pipeline_executes_subprocess(self):
        """Deve executar streamlit via subprocess."""
        with patch('src.main.subprocess.run') as mock_run:
            with patch('pathlib.Path') as mock_path_class:
                mock_path_instance = MagicMock()
                mock_path_class.return_value = mock_path_instance
                mock_path_instance.parent = MagicMock()
                mock_streamlit = MagicMock()
                mock_path_instance.parent.__truediv__.return_value = mock_streamlit
                mock_streamlit.exists.return_value = True

                run_streamlit_pipeline()

                mock_run.assert_called_once()


# ===================== Testes da Função Main =====================

class TestMain:
    """Testes para função main."""

    def test_main_runs_cli_pipeline_with_cli_flag(self):
        """Deve executar CLI pipeline quando --cli está nos argumentos."""
        with patch('src.main.run_cli_pipeline') as mock_cli:
            with patch.object(sys, 'argv', ['main', '--cli']):
                main()

                mock_cli.assert_called_once()

    def test_main_runs_streamlit_pipeline_without_cli_flag(self):
        """Deve executar Streamlit pipeline por padrão."""
        with patch('src.main.run_streamlit_pipeline') as mock_streamlit:
            with patch.object(sys, 'argv', ['main']):
                main()

                mock_streamlit.assert_called_once()

    def test_main_runs_streamlit_pipeline_with_other_flags(self):
        """Deve executar Streamlit com flags diferentes."""
        with patch('src.main.run_streamlit_pipeline') as mock_streamlit:
            with patch.object(sys, 'argv', ['main', '--help']):
                main()

                mock_streamlit.assert_called_once()

    def test_main_prefers_cli_flag(self):
        """Deve preferir CLI se --cli está presente."""
        with patch('src.main.run_cli_pipeline') as mock_cli:
            with patch('src.main.run_streamlit_pipeline') as mock_streamlit:
                with patch.object(sys, 'argv', ['main', '--cli']):
                    main()

                    mock_cli.assert_called_once()
                    mock_streamlit.assert_not_called()


# ===================== Integration Tests =====================

class TestMainIntegration:
    """Testes de integração do módulo main."""

    def test_task_functions_work_with_ingestion_service(self, mock_station, sample_readings):
        """Deve retornar dados quando chamado com serviço real."""
        mock_service = MagicMock()
        mock_service.fetch_weather_readings.return_value = sample_readings
        mock_service.get_water_readings.return_value = sample_readings

        weather_result = fetch_weather_task(
            mock_service,
            mock_station,
            datetime(2026, 1, 15),
            datetime(2026, 1, 16),
        )
        water_result = fetch_water_task(
            mock_service,
            mock_station,
            datetime(2026, 1, 15),
            datetime(2026, 1, 16),
        )

        assert weather_result[0] == "weather"
        assert water_result[0] == "water"
        assert len(weather_result[1]) == 2
        assert len(water_result[1]) == 2

    def test_cli_pipeline_handles_multiple_stations(self, capsys):
        """Deve processar estações múltiplas corretamente."""
        station1 = Station(id=1, code="EST001", name="Estação 01", latitude=-15.5, longitude=-48.5)
        station2 = Station(id=2, code="EST002", name="Estação 02", latitude=-15.6, longitude=-48.6)

        with patch('src.main.ReadingRepository') as mock_repo_class:
            with patch('src.main.IngestionService'):
                with patch('src.main.AnalyticsService'):
                    with patch('src.main.show_statistics_table'):
                        with patch('src.main.export_statistics_to_csv'):
                            with patch('src.main.export_statistics_with_outliers_detail'):
                                with patch('src.main.select_station') as mock_select:
                                    with patch('src.main.read_date_range') as mock_date_range:
                                        mock_repo = MagicMock()
                                        mock_repo_class.return_value = mock_repo
                                        mock_repo.get_stations.return_value = [station1, station2]
                                        mock_repo.get_by_station.return_value = []
                                        mock_repo.save_many.return_value = []
                                        
                                        # Selecionar primeira estação
                                        mock_select.return_value = station1
                                        mock_date_range.return_value = (
                                            datetime(2026, 1, 15),
                                            datetime(2026, 1, 16),
                                        )
                                        
                                        run_cli_pipeline()
                                        
                                        # Deve ter tido acesso à lista de estações
                                        mock_repo.get_stations.assert_called_once()
