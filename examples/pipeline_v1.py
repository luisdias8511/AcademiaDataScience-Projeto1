"""Pipeline v1: Fluxo completo simples para estudantes iniciantes.

Demonstra o fluxo de ponta a ponta:
Escolha de Estação → Período → Ingestion → Persistência → Recuperação → Analytics → Tabela
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

# Adicionar raiz do projeto ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.database.reading_repository import ReadingRepository
from src.ingestion.mock_service import MockIngestionService
from src.analytics.mock_service import MockAnalyticsService
from src.presentation import (
    show_stations,
    select_station,
    read_date_range,
    show_statistics_table,
)
# FUNÇÃO PRINCIPAL
# ============================================================================

def main():
    """Função principal que orquestra o pipeline completo."""
    try:
        print("\n" + "=" * 90)
        print("PIPELINE V1 - Análise de Dados Ambientais")
        print("=" * 90)

        # ====================================================================
        # ETAPA 1: CONECTAR AO REPOSITÓRIO E LISTAR ESTAÇÕES
        # ====================================================================
        print("\n[1/8] Conectando ao banco de dados...")
        repository = ReadingRepository()
        print("✓ Conexão estabelecida")

        print("\n[2/8] Buscando estações...")
        stations = repository.get_stations()
        
        if not stations:
            print("❌ Nenhuma estação cadastrada no banco.")
            return
        
        print(f"✓ {len(stations)} estação(ões) encontrada(s)")
        show_stations(stations)

        # ====================================================================
        # ETAPA 2: SELECIONAR ESTAÇÃO
        # ====================================================================
        print("\n[3/8] Selecionando estação...")
        selected_station = select_station(stations)

        # ====================================================================
        # ETAPA 3: INFORMAR PERÍODO
        # ====================================================================
        print("\n[4/8] Informando período...")
        start_date, end_date = read_date_range()

        # ====================================================================
        # ETAPA 4: INGESTION MOCK
        # ====================================================================
        print("\n[5/8] Ingestão de dados...")
        ingestion_service = MockIngestionService()
        readings = ingestion_service.get_readings(selected_station, start_date, end_date)
        print(f"✓ {len(readings)} reading(s) coletado(s)")

        # ====================================================================
        # ETAPA 5: PERSISTÊNCIA (SAVE_MANY)
        # ====================================================================
        print("\n[6/8] Persistindo dados no banco...")
        reading_ids = repository.save_many(readings, parameter_category_id=1)
        print(f"✓ {len(reading_ids)} leitura(s) persistida(s)")

        # ====================================================================
        # ETAPA 6: RECUPERAÇÃO DE DADOS
        # ====================================================================
        print("\n[7/8] Recuperando dados do período...")
        persisted_readings = repository.get_by_station(
            selected_station.id,
            start_date,
            end_date
        )
        print(f"✓ {len(persisted_readings)} leitura(s) recuperada(s)")

        # ====================================================================
        # ETAPA 7: ANALYTICS MOCK
        # ====================================================================
        print("\n[8/8] Calculando estatísticas...")
        analytics_service = MockAnalyticsService()
        statistics = analytics_service.calculate(persisted_readings)
        print(f"✓ Estatísticas calculadas para {len(statistics)} parâmetro(s)")

        # ====================================================================
        # ETAPA 8: EXIBIR RESULTADOS
        # ====================================================================
        show_statistics_table(statistics)

        print("\n" + "=" * 90)
        print("✓ PIPELINE CONCLUÍDO COM SUCESSO")
        print("=" * 90 + "\n")

    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
