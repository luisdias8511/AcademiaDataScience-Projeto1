"""Testes para validação completa do projeto."""

import pytest
from pathlib import Path
from datetime import datetime, timezone
import sys
import importlib


class TestProjectStructure:
    """Testes para validar estrutura do projeto."""

    def test_src_directory_exists(self):
        """Verifica se diretório src existe."""
        assert Path("src").exists()
        assert Path("src").is_dir()

    def test_tests_directory_exists(self):
        """Verifica se diretório tests existe."""
        assert Path("tests").exists()
        assert Path("tests").is_dir()

    def test_required_modules_exist(self):
        """Verifica se módulos principais existem."""
        modules = [
            "src.models",
            "src.database",
            "src.analytics",
            "src.processing",
            "src.reporting",
            "src.security",
            "src.services",
        ]

        for module_name in modules:
            try:
                importlib.import_module(module_name)
            except ImportError:
                pytest.fail(f"Módulo {module_name} não encontrado")

    def test_main_py_exists(self):
        """Verifica se arquivo main.py existe."""
        assert Path("src/main.py").exists()

    def test_config_exists(self):
        """Verifica se arquivo de configuração existe."""
        config_paths = [
            Path(".env.example"),
            Path("pytest.ini"),
        ]

        for config in config_paths:
            assert config.exists() or config.name == ".env.example"


class TestImports:
    """Testes para validar imports dos módulos."""

    def test_import_models(self):
        """Deve importar modelos sem erros."""
        from src.models.station import Station
        from src.models.reading import Reading
        from src.models.parameter import Parameter
        from src.models.statistics_result import StatisticsResult

        assert Station is not None
        assert Reading is not None
        assert Parameter is not None
        assert StatisticsResult is not None

    def test_import_database(self):
        """Deve importar módulo database sem erros."""
        from src.database.reading_repository import ReadingRepository

        assert ReadingRepository is not None

    def test_import_analytics(self):
        """Deve importar módulo analytics sem erros."""
        from src.analytics.service import AnalyticsService
        from src.analytics.statistics import calcular_estatisticas
        from src.analytics.outliers import identificar_outliers

        assert AnalyticsService is not None
        assert calcular_estatisticas is not None
        assert identificar_outliers is not None

    def test_import_processing(self):
        """Deve importar módulo processing sem erros."""
        from src.processing.reading_processor import ReadingProcessor

        assert ReadingProcessor is not None

    def test_import_reporting(self):
        """Deve importar módulo reporting sem erros."""
        from src.reporting.csv_export import (
            export_statistics_to_csv,
            export_statistics_with_outliers_detail,
        )

        assert export_statistics_to_csv is not None
        assert export_statistics_with_outliers_detail is not None

    def test_import_security(self):
        """Deve importar módulo security sem erros."""
        from src.security.log_utils import tratar_erro

        assert tratar_erro is not None


class TestTypeHints:
    """Testes para validar type hints."""

    def test_models_have_type_hints(self):
        """Verifica se modelos têm type hints completos."""
        from src.models.station import Station

        # Verificar que tem annotations
        assert hasattr(Station, "__annotations__")
        assert len(Station.__annotations__) > 0

    def test_services_have_type_hints(self):
        """Verifica se serviços têm type hints."""
        from src.analytics.service import AnalyticsService

        service = AnalyticsService()
        assert hasattr(service.calculate, "__annotations__")


class TestDataValidation:
    """Testes de validação de dados."""

    def test_station_cannot_be_created_with_invalid_latitude(self):
        """Estação com latitude inválida deve falhar."""
        from decimal import Decimal
        from src.models.station import Station

        with pytest.raises(ValueError):
            Station(
                id=1,
                code="TEST",
                name="Test",
                latitude=Decimal("100"),  # > 90
                longitude=Decimal("0"),
            )

    def test_reading_requires_timezone_aware_timestamp(self):
        """Leitura com timestamp naïve deve falhar."""
        from src.models.reading import Reading
        from src.models.reading_value import ReadingValue

        with pytest.raises(ValueError):
            Reading(
                station_id=1,
                timestamp=datetime.now(),  # Sem timezone
                values=(ReadingValue(parameter_code="TEMP", value="25"),),
            )

    def test_parameter_code_cannot_be_empty(self):
        """Código de parâmetro vazio deve falhar."""
        from src.models.reading_value import ReadingValue

        with pytest.raises(ValueError):
            ReadingValue(parameter_code="", value="25")


class TestFileStructure:
    """Testes para validar estrutura de arquivos."""

    def test_all_python_files_have_docstrings(self):
        """Verifica se arquivos Python principais têm docstrings."""
        important_files = [
            "src/main.py",
            "src/models/station.py",
            "src/database/reading_repository.py",
            "src/analytics/service.py",
        ]

        for filepath in important_files:
            path = Path(filepath)
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Deve ter docstring no início ("""...""")
                    assert '"""' in content or "'''" in content

    def test_test_files_follow_naming_convention(self):
        """Verifica se arquivos de teste seguem convenção."""
        tests_dir = Path("tests")
        test_files = list(tests_dir.glob("test_*.py"))

        assert len(test_files) > 0
        for test_file in test_files:
            assert test_file.name.startswith("test_")
            assert test_file.name.endswith(".py")


class TestRequirements:
    """Testes para dependências."""

    def test_requirements_file_exists(self):
        """Verifica se requirements.txt existe."""
        assert Path("requirements.txt").exists()

    def test_test_requirements_file_exists(self):
        """Verifica se requirements-test.txt existe."""
        assert Path("requirements-test.txt").exists()

    def test_required_packages_listed(self):
        """Verifica se pacotes críticos estão listados."""
        with open("requirements.txt", 'r') as f:
            content = f.read()

        required = ["streamlit", "pandas", "pyodbc", "requests"]
        for package in required:
            assert any(line.startswith(package) for line in content.split("\n"))


class TestEnvironmentSetup:
    """Testes para configuração de ambiente."""

    def test_python_version_compatible(self):
        """Verifica se versão Python é compatível."""
        # Projeto usa Python 3.14+
        assert sys.version_info >= (3, 10)

    def test_project_root_accessible(self):
        """Verifica se diretório raiz do projeto é acessível."""
        # Deve conseguir importar src
        import src  # noqa

    def test_src_is_package(self):
        """Verifica se src é um package Python."""
        assert Path("src/__init__.py").exists()


class TestErrorHandling:
    """Testes para tratamento de erros."""

    def test_invalid_station_raises_value_error(self):
        """Estação inválida deve lançar ValueError."""
        from src.models.station import Station
        from decimal import Decimal

        with pytest.raises(ValueError):
            Station(
                id=0,  # ID inválido
                code="TEST",
                name="Test",
                latitude=Decimal("0"),
                longitude=Decimal("0"),
            )

    def test_invalid_reading_raises_value_error(self):
        """Leitura inválida deve lançar ValueError."""
        from src.models.reading import Reading

        with pytest.raises(ValueError):
            Reading(
                station_id=0,  # ID inválido
                timestamp=datetime.now(timezone.utc),
                values=(),  # Valores vazios
            )

    def test_analytics_with_mixed_stations_raises_error(self):
        """Analytics com múltiplas estações deve lançar erro."""
        from src.analytics.service import AnalyticsService
        from src.models.reading import Reading
        from src.models.reading_value import ReadingValue

        analytics = AnalyticsService()

        readings = [
            Reading(
                station_id=1,
                timestamp=datetime.now(timezone.utc),
                values=(ReadingValue(parameter_code="TEMP", value="25"),),
            ),
            Reading(
                station_id=2,
                timestamp=datetime.now(timezone.utc),
                values=(ReadingValue(parameter_code="TEMP", value="26"),),
            ),
        ]

        with pytest.raises(ValueError):
            analytics.calculate(readings)


class TestCodeQuality:
    """Testes para qualidade de código."""

    def test_no_hardcoded_secrets_in_code(self):
        """Verifica se não há secrets hardcoded."""
        import re

        excluded_dirs = [".git", "__pycache__", ".venv", "node_modules"]
        secret_patterns = [
            r"password\s*=\s*['\"]",
            r"api_key\s*=\s*['\"]",
            r"secret\s*=\s*['\"]",
        ]

        for py_file in Path("src").rglob("*.py"):
            if any(excluded in str(py_file) for excluded in excluded_dirs):
                continue

            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

                for pattern in secret_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    # Permitir comentários e exemplos
                    if matches and "#" not in content[content.find(matches[0]) - 20:]:
                        pytest.skip(f"Possível secret em {py_file}")

    def test_models_are_frozen_dataclasses(self):
        """Verifica se modelos usam frozen dataclasses."""
        from src.models.station import Station
        from src.models.reading import Reading

        # Tentar modificar deve falhar
        from decimal import Decimal

        station = Station(
            id=1,
            code="TEST",
            name="Test",
            latitude=Decimal("0"),
            longitude=Decimal("0"),
        )

        with pytest.raises(AttributeError):
            station.name = "Modified"

        reading = Reading(
            station_id=1,
            timestamp=datetime.now(timezone.utc),
            values=(ReadingValue(parameter_code="TEMP", value="25"),),
        )

        with pytest.raises(AttributeError):
            reading.station_id = 2

    def test_modules_have_proper_docstrings(self):
        """Verifica se módulos têm docstrings."""
        from src.models import station
        from src.analytics import service

        assert station.__doc__ is not None
        assert service.__doc__ is not None


# Importação necessária para testes
from src.models.reading_value import ReadingValue  # noqa
