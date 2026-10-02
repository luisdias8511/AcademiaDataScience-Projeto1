"""Script para executar testes automatizados com diferentes configurações."""

import subprocess
import sys
from pathlib import Path


def run_tests(coverage=False, verbose=False, specific_test=None):
    """Executa os testes com a configuração especificada.
    
    Args:
        coverage: Se True, gera relatório de cobertura de código
        verbose: Se True, aumenta verbosidade da saída
        specific_test: Se fornecido, executa apenas esse teste
    """
    cmd = [sys.executable, "-m", "pytest"]
    
    if specific_test:
        cmd.append(specific_test)
    
    if verbose:
        cmd.append("-vv")
    else:
        cmd.append("-v")
    
    if coverage:
        cmd.extend([
            "--cov=src",
            "--cov-report=html",
            "--cov-report=term-missing"
        ])
    
    print(f"Executando: {' '.join(cmd)}")
    print("=" * 80)
    
    result = subprocess.run(cmd)
    return result.returncode


def run_by_marker(marker):
    """Executa testes marcados com um marcador específico.
    
    Args:
        marker: Nome do marcador (unit, integration, slow, etc)
    """
    cmd = [sys.executable, "-m", "pytest", "-m", marker, "-v"]
    print(f"Executando testes com marcador: {marker}")
    print("=" * 80)
    result = subprocess.run(cmd)
    return result.returncode


def main():
    """Função principal para interpretação de argumentos."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Executor de testes automatizados"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Gerar relatório de cobertura"
    )
    parser.add_argument(
        "--verbose", "-vv",
        action="store_true",
        help="Aumentar verbosidade"
    )
    parser.add_argument(
        "--test",
        help="Executar teste específico"
    )
    parser.add_argument(
        "--marker", "-m",
        help="Executar testes com marcador específico"
    )
    parser.add_argument(
        "--unit",
        action="store_true",
        help="Executar apenas testes unitários"
    )
    parser.add_argument(
        "--integration",
        action="store_true",
        help="Executar apenas testes de integração"
    )
    parser.add_argument(
        "--database",
        action="store_true",
        help="Executar apenas testes de banco de dados"
    )
    parser.add_argument(
        "--analytics",
        action="store_true",
        help="Executar apenas testes de analytics"
    )
    
    args = parser.parse_args()
    
    # Se nenhuma opção específica, rodar todos os testes
    if args.test:
        return run_tests(coverage=args.coverage, verbose=args.verbose, specific_test=args.test)
    elif args.unit:
        return run_by_marker("unit")
    elif args.integration:
        return run_by_marker("integration")
    elif args.database:
        return run_by_marker("database")
    elif args.analytics:
        return run_by_marker("analytics")
    elif args.marker:
        return run_by_marker(args.marker)
    else:
        return run_tests(coverage=args.coverage, verbose=args.verbose)


if __name__ == "__main__":
    sys.exit(main())
