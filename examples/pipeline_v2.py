"""Pipeline v2: Fluxo completo com dados de weather e water.

Demonstra o fluxo de ponta a ponta com dois tipos de dados ambientais:
Escolha de Estação → Período → Ingestion (Weather + Water) → Persistência → Recuperação + Filtros → Analytics → Tabelas
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

# Adicionar raiz do projeto ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database.reading_repository import ReadingRepository
from src.services.api_weather_service import IngestionService
from src.analytics.service import AnalyticsService # alteração de mock para analytics.service
from src.presentation import (
    show_stations,
    select_station,
    read_date_range,
    show_statistics_table,
)
# FUNÇÃO PRINCIPAL
# ============================================================================

def main():
    """Função principal que orquestra o pipeline completo com weather e water."""
    try:
        print("\n" + "=" * 90)
        print("PIPELINE V2 - Análise de Dados Ambientais (Weather + Water)")
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
        # ETAPA 4: INGESTION METEOROLÓGICA
        # ====================================================================
        print("\n[5/11] Ingestão de dados meteorológicos...")
        ingestion_service = IngestionService()
        weather_readings = ingestion_service.get_readings(selected_station, start_date, end_date)
        print(f"✓ {len(weather_readings)} reading(s) meteorológico(s) coletado(s)")

        # ====================================================================
        # ETAPA 5: INGESTION DE ÁGUA
        # ====================================================================
        print("\n[6/11] Ingestão de dados de qualidade da água...")
        water_readings = ingestion_service.get_water_readings(selected_station, start_date, end_date)
        print(f"✓ {len(water_readings)} reading(s) de água coletado(s)")

        # ====================================================================
        # ETAPA 7: PERSISTÔNCIA METEOROLÓGICA
        # ====================================================================
        print("\n[7/11] Persistindo dados meteorológicos no banco...")
        weather_ids = repository.save_many(weather_readings, parameter_category_id=1)
        print(f"✓ {len(weather_ids)} leitura(s) meteorológica(s) persistida(s)")

        # ====================================================================
        # ETAPA 8: PERSISTÔNCIA DE ÁGUA
        # ====================================================================
        print("\n[8/11] Persistindo dados de água no banco...")
        water_ids = repository.save_many(water_readings, parameter_category_id=2)
        print(f"✓ {len(water_ids)} leitura(s) de água persistida(s)")

        # ====================================================================
        # ETAPA 8: RECUPERAÇÃO DE DADOS DO PERÍODO
        # ====================================================================
        print("\n[9/11] Recuperando dados do período...")
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
        # ETAPA 10: ANALYTICS METEOROLÓGICO
        # ====================================================================
        print("\n[10/11] Calculando estatísticas (weather + water)...")
        analytics_service = AnalyticsService() # alteração para usar novo módulo AnalyticsService
        weather_statistics = analytics_service.calculate(weather_only)
        print(f"✓ Estatísticas meteorológicas calculadas para {len(weather_statistics)} parâmetro(s)")

        # ====================================================================
        # ETAPA 11: ANALYTICS DE ÁGUA
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

        print("\n" + "-" * 90)
        print("RESULTADOS - QUALIDADE DA ÁGUA")
        print("-" * 90)
        show_statistics_table(water_statistics)

        print("\n" + "=" * 90)
        print("✓ PIPELINE CONCLUÍDO COM SUCESSO")
        print("=" * 90 + "\n")

    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
