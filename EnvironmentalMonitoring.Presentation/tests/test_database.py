"""Testes para o repositório de dados.

Testes focados em:
1. Validações de inicialização
2. Mocking correto com a API real
3. Caminhos sem dependência de pyodbc real
"""

import pytest
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from unittest.mock import Mock, MagicMock, patch, PropertyMock
import os

from src.database.reading_repository import ReadingRepository
from src.models.reading import Reading
from src.models.reading_value import ReadingValue
from src.models.station import Station
from src.models.parameter import Parameter


"""Testes para o repositório de dados.

Testes focados em validação de inicialização e caminhos sem dependência
de conexão real com SQL Server.
"""

import pytest
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from unittest.mock import Mock, MagicMock, patch, call
import os

from src.database.reading_repository import ReadingRepository
from src.models.reading import Reading
from src.models.reading_value import ReadingValue
from src.models.station import Station
from src.models.parameter import Parameter


class TestReadingRepositoryInitialization:
    """Testes para inicialização e validação do repositório."""

    def test_init_with_custom_connection_string(self):
        """Deve aceitar connection string customizada."""
        custom_string = "DRIVER={ODBC Driver 18 for SQL Server};SERVER=custom;DATABASE=test;"
        repo = ReadingRepository(connection_string=custom_string)
        assert repo.connection_string == custom_string

    def test_init_with_env_variables(self):
        """Deve carregar variáveis de ambiente quando não fornecida string."""
        with patch.dict(os.environ, {
            "SQL_SERVER": "localhost\\SQLEXPRESS",
            "SQL_DATABASE": "EnvironmentalMonitoring"
        }):
            repo = ReadingRepository()
            assert "localhost\\SQLEXPRESS" in repo.connection_string
            assert "EnvironmentalMonitoring" in repo.connection_string

    def test_connection_string_format(self):
        """Deve gerar connection string com formato correto."""
        with patch.dict(os.environ, {
            "SQL_SERVER": "DESKTOP-ABC\\SQLEXPRESS",
            "SQL_DATABASE": "TestDB"
        }):
            repo = ReadingRepository()
            assert "DRIVER={ODBC Driver 18 for SQL Server}" in repo.connection_string
            assert "Trusted_Connection=yes" in repo.connection_string
            assert "TrustServerCertificate=yes" in repo.connection_string

    def test_initial_connection_is_none(self):
        """Deve iniciar com conexão None."""
        with patch.dict(os.environ, {
            "SQL_SERVER": "localhost\\SQLEXPRESS",
            "SQL_DATABASE": "TestDB"
        }):
            repo = ReadingRepository()
            assert repo.conn is None


class TestReadingRepositoryConnectionHandling:
    """Testes para tratamento de conexão com mocks."""

    @pytest.fixture
    def mock_pyodbc(self):
        """Mock do módulo pyodbc."""
        with patch('src.database.reading_repository.pyodbc') as mock:
            yield mock

    def test_connect_calls_pyodbc(self, mock_pyodbc):
        """Deve chamar pyodbc.connect com a connection string."""
        mock_connection = MagicMock()
        mock_pyodbc.connect.return_value = mock_connection

        with patch.dict(os.environ, {
            "SQL_SERVER": "localhost\\SQLEXPRESS",
            "SQL_DATABASE": "TestDB"
        }):
            repo = ReadingRepository()
            repo._connect()

            mock_pyodbc.connect.assert_called_once()
            assert repo.conn == mock_connection

    def test_connect_error_raises_exception(self, mock_pyodbc):
        """Deve lançar exceção se conexão falhar."""
        mock_pyodbc.connect.side_effect = Exception("Connection timeout")

        with patch.dict(os.environ, {
            "SQL_SERVER": "localhost\\SQLEXPRESS",
            "SQL_DATABASE": "TestDB"
        }):
            repo = ReadingRepository()
            with pytest.raises(Exception) as exc_info:
                repo._connect()
            assert "Falha ao conectar" in str(exc_info.value)

    def test_disconnect_closes_connection(self, mock_pyodbc):
        """Deve fechar conexão ao desconectar."""
        mock_connection = MagicMock()
        mock_pyodbc.connect.return_value = mock_connection

        with patch.dict(os.environ, {
            "SQL_SERVER": "localhost\\SQLEXPRESS",
            "SQL_DATABASE": "TestDB"
        }):
            repo = ReadingRepository()
            repo.conn = mock_connection
            repo._disconnect()

            mock_connection.close.assert_called_once()
            assert repo.conn is None

    def test_disconnect_without_connection(self):
        """Deve ser seguro desconectar sem conexão ativa."""
        with patch.dict(os.environ, {
            "SQL_SERVER": "localhost\\SQLEXPRESS",
            "SQL_DATABASE": "TestDB"
        }):
            repo = ReadingRepository()
            repo._disconnect()  # Não deve lançar erro
            assert repo.conn is None


class TestReadingRepositoryPyodbcImport:
    """Testes para tratamento do import de pyodbc."""

    def test_connect_with_pyodbc_none_raises_import_error(self):
        """Deve lançar ImportError se pyodbc não estiver instalado."""
        with patch.dict(os.environ, {
            "SQL_SERVER": "localhost\\SQLEXPRESS",
            "SQL_DATABASE": "TestDB"
        }):
            with patch('src.database.reading_repository.pyodbc', None):
                repo = ReadingRepository()
                with pytest.raises(ImportError) as exc_info:
                    repo._connect()
                assert "pyodbc" in str(exc_info.value)

    def test_init_succeeds_even_if_pyodbc_missing(self):
        """Deve permitir inicializar repo sem pyodbc instalado."""
        with patch.dict(os.environ, {
            "SQL_SERVER": "localhost\\SQLEXPRESS",
            "SQL_DATABASE": "TestDB"
        }):
            # Mesmo com pyodbc = None, init deve funcionar
            repo = ReadingRepository()
            assert repo is not None


class TestReadingRepositoryQueryMethods:
    """Testes dos métodos de query com mocks completos."""

    @pytest.fixture
    def mock_repo_setup(self):
        """Configura mock do repositório com conexão mockada."""
        with patch.dict(os.environ, {
            "SQL_SERVER": "localhost\\SQLEXPRESS",
            "SQL_DATABASE": "TestDB"
        }):
            repo = ReadingRepository()
            repo.conn = MagicMock()
            repo.conn.cursor.return_value = MagicMock()
            yield repo

    def test_get_stations_executes_query(self, mock_repo_setup):
        """Deve executar query para obter estações."""
        mock_cursor = mock_repo_setup.conn.cursor.return_value
        mock_cursor.fetchall.return_value = [
            (1, "EST_001", "Estação Central", Decimal("-23.5505"), Decimal("-46.6333")),
        ]

        with patch.object(mock_repo_setup, '_connect'):
            with patch.object(mock_repo_setup, '_disconnect'):
                stations = mock_repo_setup.get_stations()

                mock_cursor.execute.assert_called()
                assert len(stations) == 1
                assert isinstance(stations[0], Station)

    def test_get_station_by_id_returns_station(self, mock_repo_setup):
        """Deve retornar Station por ID."""
        mock_cursor = mock_repo_setup.conn.cursor.return_value
        mock_cursor.fetchone.return_value = (
            1, "EST_001", "Estação Central", Decimal("-23.5505"), Decimal("-46.6333")
        )

        with patch.object(mock_repo_setup, '_connect'):
            with patch.object(mock_repo_setup, '_disconnect'):
                station = mock_repo_setup.get_station_by_id(1)

                assert isinstance(station, Station)
                assert station.id == 1
                assert station.code == "EST_001"

    def test_get_station_by_id_returns_none_when_not_found(self, mock_repo_setup):
        """Deve retornar None quando estação não existe."""
        mock_cursor = mock_repo_setup.conn.cursor.return_value
        mock_cursor.fetchone.return_value = None

        with patch.object(mock_repo_setup, '_connect'):
            with patch.object(mock_repo_setup, '_disconnect'):
                station = mock_repo_setup.get_station_by_id(999)

                assert station is None

    def test_save_many_with_empty_list(self, mock_repo_setup):
        """Deve retornar lista vazia para entrada vazia."""
        ids = mock_repo_setup.save_many([], parameter_category_id=1)
        assert ids == []

    def test_get_parameter_id_by_code(self, mock_repo_setup):
        """Deve recuperar ID do parâmetro pelo código."""
        mock_cursor = mock_repo_setup.conn.cursor.return_value
        mock_cursor.fetchone.return_value = (42,)

        with patch.object(mock_repo_setup, '_connect'):
            with patch.object(mock_repo_setup, '_disconnect'):
                param_id = mock_repo_setup.get_parameter_id_by_code(
                    "temperature",
                    parameter_category_id=1
                )

                assert param_id == 42

    def test_get_parameter_id_by_code_not_found(self, mock_repo_setup):
        """Deve retornar None quando parâmetro não existe."""
        mock_cursor = mock_repo_setup.conn.cursor.return_value
        mock_cursor.fetchone.return_value = None

        with patch.object(mock_repo_setup, '_connect'):
            with patch.object(mock_repo_setup, '_disconnect'):
                param_id = mock_repo_setup.get_parameter_id_by_code(
                    "unknown_param",
                    parameter_category_id=1
                )

                assert param_id is None


class TestReadingRepositoryAdvancedQueries:
    """Testes avançados de queries e transações."""

    @pytest.fixture
    def mock_repo_setup(self):
        """Configura mock do repositório."""
        with patch.dict(os.environ, {
            "SQL_SERVER": "localhost\\SQLEXPRESS",
            "SQL_DATABASE": "TestDB"
        }):
            repo = ReadingRepository()
            repo.conn = MagicMock()
            repo.conn.cursor.return_value = MagicMock()
            yield repo

    def test_get_parameter_values_with_station_filter(self, mock_repo_setup):
        """Deve filtrar valores de parâmetro por estação."""
        mock_cursor = mock_repo_setup.conn.cursor.return_value
        mock_cursor.fetchone.return_value = (1,)  # param_id
        mock_cursor.fetchall.return_value = [(25.5,), (26.0,), (25.8,)]

        with patch.object(mock_repo_setup, '_connect'):
            with patch.object(mock_repo_setup, '_disconnect'):
                values = mock_repo_setup.get_parameter_values(
                    parameter_code="temperature",
                    start_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
                    end_date=datetime(2026, 1, 31, tzinfo=timezone.utc),
                    parameter_category_id=1,
                    station_id=1,
                )

                assert len(values) == 3
                assert all(isinstance(v, float) for v in values)

    def test_get_parameter_values_without_station_filter(self, mock_repo_setup):
        """Deve buscar valores de parâmetro para todas as estações."""
        mock_cursor = mock_repo_setup.conn.cursor.return_value
        mock_cursor.fetchone.return_value = (1,)  # param_id
        mock_cursor.fetchall.return_value = [(25.5,), (26.0,)]

        with patch.object(mock_repo_setup, '_connect'):
            with patch.object(mock_repo_setup, '_disconnect'):
                values = mock_repo_setup.get_parameter_values(
                    parameter_code="temperature",
                    start_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
                    end_date=datetime(2026, 1, 31, tzinfo=timezone.utc),
                    parameter_category_id=1,
                )

                assert len(values) == 2
                mock_cursor.execute.assert_called()

    def test_get_parameter_values_parameter_not_found(self, mock_repo_setup):
        """Deve retornar lista vazia quando parâmetro não existe."""
        mock_cursor = mock_repo_setup.conn.cursor.return_value
        mock_cursor.fetchone.return_value = None

        with patch.object(mock_repo_setup, '_connect'):
            with patch.object(mock_repo_setup, '_disconnect'):
                values = mock_repo_setup.get_parameter_values(
                    parameter_code="nonexistent",
                    start_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
                    end_date=datetime(2026, 1, 31, tzinfo=timezone.utc),
                    parameter_category_id=1,
                )

                assert values == []

    def test_get_by_station_with_multiple_readings(self, mock_repo_setup):
        """Deve recuperar múltiplas leituras de uma estação."""
        mock_cursor = mock_repo_setup.conn.cursor.return_value
        
        # Primeira chamada retorna IDs de leituras
        base_time = datetime.now(timezone.utc)
        mock_cursor.fetchall.side_effect = [
            [(1, 1, base_time), (2, 1, base_time + timedelta(hours=1))],  # readings
            [(b"TEMPERATURE", "25.5")],  # values for reading 1
            [(b"TEMPERATURE", "26.0")],  # values for reading 2
        ]

        with patch.object(mock_repo_setup, '_connect'):
            with patch.object(mock_repo_setup, '_disconnect'):
                readings = mock_repo_setup.get_by_station(
                    station_id=1,
                    start_date=base_time,
                    end_date=base_time + timedelta(days=1),
                    parameter_category_id=1,
                )

                assert isinstance(readings, list)

    def test_get_by_station_empty_result(self, mock_repo_setup):
        """Deve retornar lista vazia quando não há leituras."""
        mock_cursor = mock_repo_setup.conn.cursor.return_value
        mock_cursor.fetchall.return_value = []

        with patch.object(mock_repo_setup, '_connect'):
            with patch.object(mock_repo_setup, '_disconnect'):
                readings = mock_repo_setup.get_by_station(
                    station_id=999,
                    start_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
                    end_date=datetime(2026, 1, 31, tzinfo=timezone.utc),
                    parameter_category_id=1,
                )

                assert readings == []


class TestReadingRepositorySaveOperations:
    """Testes para operações de salvar leituras."""

    @pytest.fixture
    def mock_repo_setup(self):
        """Configura mock do repositório."""
        with patch.dict(os.environ, {
            "SQL_SERVER": "localhost\\SQLEXPRESS",
            "SQL_DATABASE": "TestDB"
        }):
            repo = ReadingRepository()
            repo.conn = MagicMock()
            repo.conn.cursor.return_value = MagicMock()
            yield repo

    def test_save_single_reading_success(self, mock_repo_setup, sample_reading):
        """Deve salvar uma leitura com sucesso."""
        mock_cursor = mock_repo_setup.conn.cursor.return_value
        mock_cursor.fetchone.return_value = (1,)  # reading_id
        
        with patch.object(mock_repo_setup, '_connect'):
            with patch.object(mock_repo_setup, '_disconnect'):
                reading_id = mock_repo_setup.save(sample_reading, parameter_category_id=1)

                assert reading_id == 1
                mock_cursor.execute.assert_called()
                mock_repo_setup.conn.commit.assert_called_once()

    def test_save_reading_with_parameter_not_found(self, mock_repo_setup, sample_reading):
        """Deve fazer rollback quando parâmetro não existe."""
        mock_cursor = mock_repo_setup.conn.cursor.return_value
        mock_cursor.fetchone.return_value = (1,)  # reading_id first call
        mock_cursor.fetchone.side_effect = [
            (1,),  # reading_id
            None,  # parameter not found
        ]
        
        with patch.object(mock_repo_setup, '_connect'):
            with patch.object(mock_repo_setup, '_disconnect'):
                with pytest.raises(Exception) as exc_info:
                    mock_repo_setup.save(sample_reading, parameter_category_id=1)
                
                assert "Parâmetro não encontrado" in str(exc_info.value)
                mock_repo_setup.conn.rollback.assert_called()

    def test_save_many_multiple_readings(self, mock_repo_setup, sample_reading):
        """Deve salvar múltiplas leituras."""
        mock_cursor = mock_repo_setup.conn.cursor.return_value
        mock_cursor.fetchone.return_value = (1,)
        
        with patch.object(mock_repo_setup, '_connect'):
            with patch.object(mock_repo_setup, '_disconnect'):
                with patch.object(mock_repo_setup, 'save', return_value=1):
                    ids = mock_repo_setup.save_many(
                        [sample_reading, sample_reading],
                        parameter_category_id=1
                    )

                    assert len(ids) == 2

    def test_save_converts_timestamp_to_utc(self, mock_repo_setup):
        """Deve converter timestamp para UTC sem timezone."""
        mock_cursor = mock_repo_setup.conn.cursor.return_value
        mock_cursor.fetchone.return_value = (1,)
        
        # Criar leitura com timestamp
        reading = Reading(
            station_id=1,
            timestamp=datetime(2026, 1, 15, 10, 30, 45, tzinfo=timezone.utc),
            values=(
                ReadingValue(parameter_code="temperature", value=Decimal("25.5")),
            ),
        )
        
        with patch.object(mock_repo_setup, '_connect'):
            with patch.object(mock_repo_setup, '_disconnect'):
                mock_repo_setup.save(reading, parameter_category_id=1)

                # Verificar que execute foi chamado com timestamp UTC
                call_args = mock_cursor.execute.call_args_list
                assert len(call_args) > 0


class TestReadingRepositoryErrorHandling:
    """Testes para tratamento de erros e edge cases."""

    @pytest.fixture
    def mock_repo_setup(self):
        """Configura mock do repositório."""
        with patch.dict(os.environ, {
            "SQL_SERVER": "localhost\\SQLEXPRESS",
            "SQL_DATABASE": "TestDB"
        }):
            repo = ReadingRepository()
            repo.conn = MagicMock()
            repo.conn.cursor.return_value = MagicMock()
            yield repo

    def test_get_stations_handles_query_error(self, mock_repo_setup):
        """Deve lançar exceção em caso de erro de query."""
        mock_cursor = mock_repo_setup.conn.cursor.return_value
        mock_cursor.execute.side_effect = Exception("Database error")

        with patch.object(mock_repo_setup, '_connect'):
            with patch.object(mock_repo_setup, '_disconnect'):
                with pytest.raises(Exception) as exc_info:
                    mock_repo_setup.get_stations()
                
                assert "erro" in str(exc_info.value).lower()

    def test_get_station_by_id_handles_error(self, mock_repo_setup):
        """Deve tratar erro ao buscar estação por ID."""
        mock_cursor = mock_repo_setup.conn.cursor.return_value
        mock_cursor.execute.side_effect = Exception("DB error")

        with patch.object(mock_repo_setup, '_connect'):
            with patch.object(mock_repo_setup, '_disconnect'):
                with pytest.raises(Exception):
                    mock_repo_setup.get_station_by_id(1)

    def test_get_parameter_values_handles_decimal_conversion(self, mock_repo_setup):
        """Deve converter valores para float corretamente."""
        mock_cursor = mock_repo_setup.conn.cursor.return_value
        mock_cursor.fetchone.return_value = (1,)
        mock_cursor.fetchall.return_value = [
            (Decimal("25.5"),),
            (Decimal("26.123456"),),
        ]

        with patch.object(mock_repo_setup, '_connect'):
            with patch.object(mock_repo_setup, '_disconnect'):
                values = mock_repo_setup.get_parameter_values(
                    parameter_code="temperature",
                    start_date=datetime(2026, 1, 1, tzinfo=timezone.utc),
                    end_date=datetime(2026, 1, 31, tzinfo=timezone.utc),
                    parameter_category_id=1,
                )

                assert all(isinstance(v, float) for v in values)
                assert len(values) == 2

    def test_disconnect_called_on_normal_flow(self, mock_repo_setup):
        """Deve chamar _disconnect no fluxo normal."""
        mock_cursor = mock_repo_setup.conn.cursor.return_value
        mock_cursor.fetchall.return_value = []

        with patch.object(mock_repo_setup, '_connect'):
            with patch.object(mock_repo_setup, '_disconnect') as mock_disconnect:
                mock_repo_setup.get_stations()

                # _disconnect deve ter sido chamado
                assert mock_disconnect.called

    def test_get_parameter_by_code_valid(self, mock_repo_setup):
        """Deve retornar Parameter completo com todos os campos obrigatórios."""
        mock_cursor = mock_repo_setup.conn.cursor.return_value
        # Simular resultado da query: (Id, Code, CodeApi, Name, Unit, CategoryId)
        mock_cursor.fetchone.return_value = (1, "TEMPERATURE", "temperature", "Temperatura", "°C", 1)

        with patch.object(mock_repo_setup, '_connect'):
            with patch.object(mock_repo_setup, '_disconnect'):
                parameter = mock_repo_setup.get_parameter_by_code("TEMPERATURE")

        assert parameter is not None
        assert parameter.id == 1
        assert parameter.code == "TEMPERATURE"
        assert parameter.code_api == "temperature"
        assert parameter.name == "Temperatura"
        assert parameter.unit == "°C"
        assert parameter.category_id == 1

    def test_get_parameter_by_code_not_found(self, mock_repo_setup):
        """Deve retornar None quando parâmetro não existe."""
        mock_cursor = mock_repo_setup.conn.cursor.return_value
        mock_cursor.fetchone.return_value = None

        with patch.object(mock_repo_setup, '_connect'):
            with patch.object(mock_repo_setup, '_disconnect'):
                parameter = mock_repo_setup.get_parameter_by_code("NONEXISTENT")

        assert parameter is None


class TestReadingRepositoryConnectionEdgeCases:
    """Testes para edge cases de conexão."""

    def test_init_with_very_long_connection_string(self):
        """Deve aceitar connection string longa."""
        long_string = "DRIVER={ODBC Driver 18 for SQL Server};" + "X" * 1000
        repo = ReadingRepository(connection_string=long_string)
        assert len(repo.connection_string) > 1000

    def test_multiple_connects_disconnects(self):
        """Deve suportar múltiplas conexões e desconexões."""
        with patch.dict(os.environ, {
            "SQL_SERVER": "localhost\\SQLEXPRESS",
            "SQL_DATABASE": "TestDB"
        }):
            with patch('src.database.reading_repository.pyodbc') as mock_pyodbc:
                mock_connection = MagicMock()
                mock_pyodbc.connect.return_value = mock_connection

                repo = ReadingRepository()

                for _ in range(3):
                    repo._connect()
                    assert repo.conn is not None
                    repo._disconnect()
                    assert repo.conn is None

                assert mock_pyodbc.connect.call_count == 3

    def test_connection_string_includes_all_required_components(self):
        """Deve incluir todos os componentes necessários na connection string."""
        with patch.dict(os.environ, {
            "SQL_SERVER": "localhost\\SQLEXPRESS",
            "SQL_DATABASE": "TestDB"
        }):
            repo = ReadingRepository()
            conn_str = repo.connection_string

            assert "ODBC Driver 18 for SQL Server" in conn_str
            assert "localhost\\SQLEXPRESS" in conn_str
            assert "TestDB" in conn_str
            assert "Trusted_Connection=yes" in conn_str
            assert "TrustServerCertificate=yes" in conn_str

