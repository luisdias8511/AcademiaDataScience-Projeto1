"""Funções auxiliares para exibição em console.

Este módulo contém funções para:
- Apresentação de dados em formato tabular
- Entrada de dados do usuário
- Validação de datas
"""

from datetime import datetime, timezone, timedelta

from src.models.station import Station
from src.models.statistics_result import StatisticsResult


def show_stations(stations: list[Station]) -> None:
    """Exibe lista de estações em formato tabular.
    
    Args:
        stations: Lista de estações
    """
    print("\n" + "=" * 90)
    print("ESTAÇÕES DISPONÍVEIS")
    print("=" * 90)
    print(f"{'ID':<5} {'CÓDIGO':<35} {'NOME':<50}")
    print("-" * 90)
    
    for station in stations:
        print(f"{station.id:<5} {station.code:<35} {station.name:<50}")
    
    print("=" * 90)


def select_station(stations: list[Station]) -> Station:
    """Solicita ao usuário que escolha uma estação.
    
    Args:
        stations: Lista de estações disponíveis
        
    Returns:
        Estação selecionada
    """
    while True:
        try:
            station_id = int(input("\nDigite o ID da estação: "))
            
            selected = next(
                (s for s in stations if s.id == station_id),
                None
            )
            
            if selected is None:
                print(f"❌ Estação com ID {station_id} não encontrada.")
                continue
                
            print(f"✓ Estação selecionada: {selected.name}")
            return selected
            
        except ValueError:
            print("❌ ID deve ser um número inteiro.")


def parse_date(date_str: str) -> datetime | None:
    """Converte string em datetime.
    
    Args:
        date_str: Data em formato AAAA-MM-DD
        
    Returns:
        datetime com timezone UTC, ou None se inválido
    """
    try:
        parsed = datetime.strptime(date_str, "%Y-%m-%d")
        return parsed.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
    except ValueError:
        return None


def read_date_range() -> tuple[datetime, datetime]:
    """Solicita datas inicial e final com validações.
    
    Validações implementadas:
    - Data final > data inicial
    - Data inicial máx. 90 dias atrás
    - Data final máx. ontem
    - Datas diferentes
    
    Returns:
        Tupla (data_inicial, data_final)
    """
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    min_date = today - timedelta(days=90)
    max_date = today - timedelta(days=1)
    
    print(f"\n⚠️  Intervalo permitido: {min_date.date()} a {max_date.date()}")
    
    while True:
        date_str = input("Digite a data inicial (AAAA-MM-DD): ").strip()
        start_date = parse_date(date_str)
        
        if start_date is None:
            print("❌ Formato inválido. Use AAAA-MM-DD")
            continue
            
        if start_date < min_date:
            print(f"❌ Data anterior ao permitido ({min_date.date()})")
            continue
            
        if start_date > max_date:
            print(f"❌ Data posterior ao permitido ({max_date.date()})")
            continue
            
        break
    
    while True:
        date_str = input("Digite a data final (AAAA-MM-DD): ").strip()
        end_date = parse_date(date_str)
        
        if end_date is None:
            print("❌ Formato inválido. Use AAAA-MM-DD")
            continue
            
        if end_date < min_date:
            print(f"❌ Data anterior ao permitido ({min_date.date()})")
            continue
            
        if end_date > max_date:
            print(f"❌ Data posterior ao permitido ({max_date.date()})")
            continue
            
        if end_date <= start_date:
            print("❌ Data final deve ser posterior à data inicial")
            continue
            
        break
    
    print(f"✓ Período: {start_date.date()} a {end_date.date()}")
    return start_date, end_date


def show_statistics_table(results: list[StatisticsResult]) -> None:
    """Exibe resultados estatísticos em formato tabular.
    
    Args:
        results: Lista com resultados estatísticos
    """
    print("\n" + "=" * 80)
    print("ANÁLISE ESTATÍSTICA")
    print("=" * 80)
    print(f"{'PARÂMETRO':<15} {'QTDE':<8} {'MÉDIA':<12} {'MEDIANA':<12} {'DESVIO':<12}")
    print("-" * 80)
    
    for result in results:
        print(
            f"{result.parameter_code:<15} "
            f"{result.count:<8} "
            f"{result.average:<12.2f} "
            f"{result.median:<12.2f} "
            f"{result.standard_deviation:<12.2f}"
        )
    
    print("=" * 80)
