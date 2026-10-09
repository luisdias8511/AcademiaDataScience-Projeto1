#!/usr/bin/env python3
"""
Verificador de Setup de Testes - Checklist de Validação

Execute este script para verificar se toda a suite de testes está pronta.
"""

import sys
from pathlib import Path
import subprocess

# Adicionar diretório raiz do projeto ao path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def check_file_exists(filepath: str, description: str) -> bool:
    """Verifica se arquivo existe."""
    exists = Path(filepath).exists()
    status = "✓" if exists else "✗"
    print(f"  {status} {description}: {filepath}")
    return exists


def check_command_exists(command: str, description: str) -> bool:
    """Verifica se comando existe."""
    try:
        subprocess.run(
            ["python", "-m", command, "--version"],
            capture_output=True,
            check=True,
        )
        print(f"  ✓ {description}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"  ✗ {description} - Execute: pip install {command}")
        return False


def main():
    """Executa checklist de validação."""
    print("=" * 80)
    print("CHECKLIST DE VALIDAÇÃO - SUITE DE TESTES")
    print("=" * 80)

    all_checks = []

    # ========================================================================
    # ARQUIVOS DE TESTE
    # ========================================================================
    print("\n[TEST FILES] ARQUIVOS DE TESTE")
    print("-" * 80)

    test_files = [
        ("tests/__init__.py", "Package marker"),
        ("tests/conftest.py", "Fixtures compartilhadas"),
        ("tests/test_models.py", "Testes de modelos"),
        ("tests/test_processing.py", "Testes de processamento"),
        ("tests/test_analytics.py", "Testes de análise"),
        ("tests/test_reporting.py", "Testes de relatórios"),
        ("tests/test_database.py", "Testes de database"),
        ("tests/test_security.py", "Testes de segurança"),
        ("tests/test_integration.py", "Testes de integração"),
        ("tests/test_edge_cases.py", "Testes de edge cases"),
        ("tests/test_project_structure.py", "Testes de estrutura"),
        ("tests/README.md", "Documentação de testes"),
    ]

    for filepath, description in test_files:
        all_checks.append(check_file_exists(filepath, description))

    # ========================================================================
    # ARQUIVOS DE CONFIGURAÇÃO
    # ========================================================================
    print("\n[CONFIG] CONFIGURAÇÃO")
    print("-" * 80)

    config_files = [
        ("pytest.ini", "Configuração do pytest"),
        ("requirements-test.txt", "Dependências de teste"),
        ("run_tests.py", "Script de execução"),
        ("TESTS_SUMMARY.py", "Resumo da suite"),
    ]

    for filepath, description in config_files:
        all_checks.append(check_file_exists(filepath, description))

    # ========================================================================
    # DEPENDÊNCIAS PYTHON
    # ========================================================================
    print("\n[PACKAGES] DEPENDÊNCIAS")
    print("-" * 80)

    packages = [
        ("pytest", "pytest"),
        ("coverage", "pytest-cov"),
        ("pytest_timeout", "pytest-timeout"),
        ("pytest_mock", "pytest-mock"),
    ]

    for module, package in packages:
        try:
            __import__(module)
            print(f"  ✓ {package}")
            all_checks.append(True)
        except ImportError:
            print(f"  ✗ {package} - Execute: pip install {package}")
            all_checks.append(False)

    # ========================================================================
    # MÓDULOS DO PROJETO
    # ========================================================================
    print("\n[MODULES] MÓDULOS DO PROJETO")
    print("-" * 80)

    modules = [
        ("src.models", "Models"),
        ("src.processing", "Processing"),
        ("src.analytics", "Analytics"),
        ("src.database", "Database"),
        ("src.reporting", "Reporting"),
        ("src.security", "Security"),
    ]

    for module_name, description in modules:
        try:
            __import__(module_name)
            print(f"  ✓ {description}: {module_name}")
            all_checks.append(True)
        except ImportError as e:
            print(f"  ✗ {description}: {module_name} - Erro: {e}")
            all_checks.append(False)

    # ========================================================================
    # RESUMO
    # ========================================================================
    print("\n" + "=" * 80)
    print("RESUMO")
    print("=" * 80)

    total = len(all_checks)
    passed = sum(all_checks)
    failed = total - passed

    print(f"\nTotal de verificações: {total}")
    print(f"✓ Passou: {passed}")
    print(f"✗ Falhou: {failed}")

    if failed == 0:
        print("\n[SUCCESS] TUDO PRONTO! Suite de testes validada com sucesso!")
        print("\nPróximos passos:")
        print("  1. python -m pytest                    # Executar todos os testes")
        print("  2. python run_tests.py --coverage      # Gerar relatório de cobertura")
        print("  3. open htmlcov/index.html             # Visualizar cobertura")
        return 0
    else:
        print("\n[WARNING] AÇÃO NECESSÁRIA")
        print(f"\nExecute os seguintes comandos:")
        print("  pip install -r requirements-test.txt")
        print("\nDepois tente novamente:")
        print("  python tests/check_setup.py")
        return 1


if __name__ == "__main__":
    sys.exit(main())
