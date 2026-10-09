"""Funções para exportar resultados de análises estatísticas para arquivos CSV."""

import csv
import os
from datetime import datetime, timezone
from pathlib import Path

from src.models.statistics_result import StatisticsResult


def ensure_output_directory() -> Path:
    """Garante que o diretório de saída existe.
    
    Returns:
        Caminho do diretório de saída (results/)
    """
    output_dir = Path("results")
    output_dir.mkdir(exist_ok=True)
    return output_dir


def generate_csv_filename(category: str) -> str:
    """Gera nome de arquivo CSV com timestamp.
    
    Args:
        category: Categoria dos dados (weather, water)
    
    Returns:
        Nome do arquivo com timestamp
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return f"statistics_{category}_{timestamp}.csv"


def export_statistics_to_csv(
    statistics: list[StatisticsResult],
    category: str
) -> str:
    """Exporta resultados estatísticos para arquivo CSV.
    
    Args:
        statistics: Lista de resultados estatísticos
        category: Categoria dos dados (weather, water)
    
    Returns:
        Caminho do arquivo gerado
    
    Raises:
        IOError: Se houver erro na escrita do arquivo
    """
    if not statistics:
        raise ValueError("Lista de estatísticas não pode estar vazia")
    
    output_dir = ensure_output_directory()
    filename = generate_csv_filename(category)
    filepath = output_dir / filename
    
    try:
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            # Definir campos do CSV
            fieldnames = [
                'parameter_code',
                'count',
                'average',
                'median',
                'standard_deviation',
                'q1',
                'q3',
                'iqr',
                'lower_bound',
                'upper_bound',
                'outliers_count',
                'outliers'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            # Escrever cada resultado como linha
            for stat in statistics:
                row = {
                    'parameter_code': stat.parameter_code,
                    'count': stat.count,
                    'average': f"{stat.average:.2f}",
                    'median': f"{stat.median:.2f}",
                    'standard_deviation': f"{stat.standard_deviation:.2f}",
                    'q1': f"{stat.q1:.2f}",
                    'q3': f"{stat.q3:.2f}",
                    'iqr': f"{stat.iqr:.2f}",
                    'lower_bound': f"{stat.lower_bound:.2f}",
                    'upper_bound': f"{stat.upper_bound:.2f}",
                    'outliers_count': len(stat.outliers),
                    'outliers': "|".join(f"{v:.2f}" for v in stat.outliers) if stat.outliers else ""
                }
                writer.writerow(row)
        
        return str(filepath)
    
    except IOError as e:
        raise IOError(f"Erro ao exportar CSV para {filepath}: {e}") from e


def export_statistics_with_outliers_detail(
    statistics: list[StatisticsResult],
    category: str
) -> str:
    """Exporta estatísticas com detalhamento de outliers em arquivo separado.
    
    Args:
        statistics: Lista de resultados estatísticos
        category: Categoria dos dados (weather, water)
    
    Returns:
        Caminho do arquivo gerado
    
    Raises:
        IOError: Se houver erro na escrita do arquivo
    """
    if not statistics:
        raise ValueError("Lista de estatísticas não pode estar vazia")
    
    output_dir = ensure_output_directory()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"outliers_{category}_{timestamp}.csv"
    filepath = output_dir / filename
    
    try:
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['parameter_code', 'outlier_value', 'lower_bound', 'upper_bound']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            # Escrever outliers por parâmetro
            for stat in statistics:
                for outlier in stat.outliers:
                    row = {
                        'parameter_code': stat.parameter_code,
                        'outlier_value': f"{outlier:.2f}",
                        'lower_bound': f"{stat.lower_bound:.2f}",
                        'upper_bound': f"{stat.upper_bound:.2f}"
                    }
                    writer.writerow(row)
        
        return str(filepath)
    
    except IOError as e:
        raise IOError(f"Erro ao exportar detalhamento de outliers para {filepath}: {e}") from e
