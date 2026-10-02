"""Pipeline Principal: Fluxo completo com dados de weather e water.

Demonstra o fluxo de ponta a ponta com dois tipos de dados ambientais:
Escolha de Estação → Período → Ingestion (Weather + Water) → Persistência → Recuperação + Filtros → Analytics → Tabelas

EXECUTAR:
- Interface Streamlit (padrão):  python -m src.main
- Interface CLI:                 python -m src.main --cli
"""

import sys
import subprocess
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.database.reading_repository import ReadingRepository
from src.services.api_weather_service import IngestionService
from src.analytics.service import AnalyticsService
from src.presentation import (
    show_stations,
    select_station,
    read_date_range,
    show_statistics_table,
)
from src.reporting import (
    export_statistics_to_csv,
    export_statistics_with_outliers_detail,
)
from src.security.log_utils import tratar_erro

# ============================================================================
# FUNÇÕES DE INGESTION PARALELA
# ============================================================================

def fetch_weather_task(ingestion_service, station, start_date, end_date):
    """Task para executar ingestion de weather em thread paralela."""
    return ("weather", ingestion_service.fetch_weather_readings(station, start_date, end_date))

def fetch_water_task(ingestion_service, station, start_date, end_date):
    """Task para executar ingestion de water em thread paralela."""
    return ("water", ingestion_service.get_water_readings(station, start_date, end_date))

# ============================================================================
# PIPELINE CLI
# ============================================================================

def run_cli_pipeline():
    """Executa o pipeline via interface de linha de comando (console)."""
    try:
        print("\n" + "=" * 90)
        print("PIPELINE PRINCIPAL - Análise de Dados Ambientais (Weather + Water)")
        print("Executando 11 etapas...")
        print("=" * 90)

        # ====================================================================
        # ETAPA 1: CONECTAR AO REPOSITÓRIO E LISTAR ESTAÇÕES
        # ====================================================================
        print("\n[1/11] Conectando ao banco de dados...")
        repository = ReadingRepository()
        print("✓ Conexão estabelecida")

        print("\n[2/11] Buscando estações...")
        stations = repository.get_stations()
        
        if not stations:
            print("❌ Nenhuma estação cadastrada no banco.")
            return
        
        print(f"✓ {len(stations)} estação(ões) encontrada(s)")
        show_stations(stations)

        # ====================================================================
        # ETAPA 2: SELECIONAR ESTAÇÃO
        # ====================================================================
        print("\n[3/11] Selecionando estação...")
        selected_station = select_station(stations)

        # ====================================================================
        # ETAPA 3: INFORMAR PERÍODO
        # ====================================================================
        print("\n[4/11] Informando período...")
        start_date, end_date = read_date_range()

        # ====================================================================
        # ETAPA 5: INGESTION PARALELA (Weather + Water)
        # ====================================================================
        print("\n[5/11] Ingestão de dados (Weather + Water)...")
        ingestion_service = IngestionService()
        weather_readings = None
        water_readings = None
        
        # Usar ThreadPoolExecutor para executar Weather e Water em paralelo
        with ThreadPoolExecutor(max_workers=2) as executor:
            # Submeter ambas as tarefas
            future_weather = executor.submit(
                fetch_weather_task, 
                ingestion_service, 
                selected_station, 
                start_date, 
                end_date
            )
            future_water = executor.submit(
                fetch_water_task, 
                ingestion_service, 
                selected_station, 
                start_date, 
                end_date
            )
            
            # Processar resultados conforme completam
            for future in as_completed([future_weather, future_water]):
                tipo, readings = future.result()
                if tipo == "weather":
                    weather_readings = readings
                    print(f"  ✓ {len(weather_readings)} reading(s) meteorológico(s) coletado(s)")
                elif tipo == "water":
                    water_readings = readings
                    print(f"  ✓ {len(water_readings)} reading(s) de água coletado(s)")

        # ====================================================================
        # ETAPA 6: PERSISTÔNCIA METEOROLÓGICA
        # ====================================================================
        print("\n[6/11] Persistindo dados meteorológicos no banco...")
        weather_ids = repository.save_many(weather_readings, parameter_category_id=1)
        print(f"✓ {len(weather_ids)} leitura(s) meteorológica(s) persistida(s)")

        # ====================================================================
        # ETAPA 7: PERSISTÔNCIA DE ÁGUA
        # ====================================================================
        print("\n[7/11] Persistindo dados de água no banco...")
        water_ids = repository.save_many(water_readings, parameter_category_id=2)
        print(f"✓ {len(water_ids)} leitura(s) de água persistida(s)")

        # ====================================================================
        # ETAPA 8: RECUPERAÇÃO DE DADOS DO PERÍODO
        # ====================================================================
        print("\n[8/11] Recuperando dados do período...")
        # Filtrar apenas meteorológicos (temperatura, umidade, etc)
        weather_only = repository.get_by_station(
            selected_station.id,
            start_date,
            end_date,
            parameter_category_id=1
        )

        # Filtrar apenas de água (pH, turbidez, etc)
        water_only = repository.get_by_station(
            selected_station.id,
            start_date,
            end_date,
            parameter_category_id=2
        )

        # ====================================================================
        # ETAPA 9: ANALYTICS METEOROLÓGICO
        # ====================================================================
        print("\n[9/11] Calculando estatísticas (weather + water)...")
        analytics_service = AnalyticsService()
        weather_statistics = analytics_service.calculate(weather_only)
        print(f"✓ Estatísticas meteorológicas calculadas para {len(weather_statistics)} parâmetro(s)")

        # ====================================================================
        # ETAPA 10: ANALYTICS DE ÁGUA
        # ====================================================================

        water_statistics = analytics_service.calculate(water_only)
        print(f"✓ Estatísticas de água calculadas para {len(water_statistics)} parâmetro(s)")

        # ====================================================================
        # ETAPA 11: EXIBIR RESULTADOS
        # ====================================================================
        print("\n[11/11] Exibindo resultados...")
        print("\n" + "-" * 90)
        print("RESULTADOS - DADOS METEOROLÓGICOS")
        print("-" * 90)
        show_statistics_table(weather_statistics)
        
        # Exportar estatísticas meteorológicas para CSV
        weather_csv_path = export_statistics_to_csv(weather_statistics, "weather")
        weather_outliers_path = export_statistics_with_outliers_detail(weather_statistics, "weather")
        print(f"\n✓ Dados meteorológicos exportados para:")
        print(f"  - {weather_csv_path}")
        print(f"  - {weather_outliers_path}")

        print("\n" + "-" * 90)
        print("RESULTADOS - QUALIDADE DA ÁGUA")
        print("-" * 90)
        show_statistics_table(water_statistics)
        
        # Exportar estatísticas de água para CSV
        water_csv_path = export_statistics_to_csv(water_statistics, "water")
        water_outliers_path = export_statistics_with_outliers_detail(water_statistics, "water")
        print(f"\n✓ Dados de qualidade da água exportados para:")
        print(f"  - {water_csv_path}")
        print(f"  - {water_outliers_path}")

        print("\n" + "=" * 90)
        print("✓ PIPELINE CONCLUÍDO COM SUCESSO")
        print("=" * 90 + "\n")

    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        tratar_erro(e, "Falha durante execução do pipeline principal", encerrar=True)


# ============================================================================
# PIPELINE STREAMLIT
# ============================================================================

def run_streamlit_pipeline():
    """Executa o pipeline via interface Streamlit (Web UI)."""
    import os
    from pathlib import Path
    
    # Obter caminho do arquivo streamlit_app.py
    streamlit_app = Path(__file__).parent / "presentation" / "streamlit_app.py"
    
    if not streamlit_app.exists():
        print(f"❌ Erro: Arquivo {streamlit_app} não encontrado")
        return
    
    print(f"\n🚀 Iniciando interface Streamlit...")
    print(f"📂 Aplicação: {streamlit_app}\n")
    
    # Executar streamlit
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(streamlit_app)])


# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def main():
    """Função principal que escolhe entre CLI ou Streamlit."""
    # Verificar se usuário solicitou modo CLI
    if "--cli" in sys.argv:
        run_cli_pipeline()
    else:
        # Por padrão, executar Streamlit
        run_streamlit_pipeline()


if __name__ == "__main__":
    main()
