r"""Exemplo completo: Persistindo uma leitura ambiental com ReadingRepository.save()

Este exemplo demonstra como utilizar o método save() do ReadingRepository
para persistir dados ambientais no SQL Server.

PRÉ-REQUISITOS:
===============
1. SQL Server Express instalado e rodando
2. ODBC Driver 18 for SQL Server instalado
3. Banco 'EnvironmentalMonitoring' criado (sql/CREATE_DATABASE.sql)
4. Tabelas criadas (sql/CREATE_TABLES.sql)
5. Dados iniciais carregados (sql/POPULATE_DATABASE.sql)
6. Windows Authentication habilitado
7. Variáveis de ambiente configuradas no arquivo .env

VARIÁVEIS DE AMBIENTE:
======================
SQL_SERVER         - Nome/IP do SQL Server (ex: localhost\\SQLEXPRESS)
SQL_DATABASE       - Nome do banco (ex: EnvironmentalMonitoring)

EXEMPLO DE .env:
================
SQL_SERVER=localhost\\SQLEXPRESS
SQL_DATABASE=EnvironmentalMonitoring

EXECUTAR:
=========
python examples/save_reading_example.py

SAÍDA ESPERADA:
===============
✓ Conexão com banco bem-sucedida
✓ Estação encontrada: [code] - [name]
✓ Leitura persistida com sucesso. ID=123
✓ Recuperação de dados confirmada:
    Parâmetro: TEMPERATURE | Valor: 21.06 | Unidade: °C
    Parâmetro: HUMIDITY | Valor: 65.50 | Unidade: %
    ...
"""

import sys
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from pathlib import Path

# Adicionar raiz do projeto ao path
# Permite executar o script de qualquer diretório
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Importar classes necessárias
from src.database.reading_repository import ReadingRepository
from src.models.reading import Reading
from src.models.reading_value import ReadingValue


def main():
    """Função principal que demonstra o fluxo completo."""
    try:
        # ====================================================================
        # ETAPA 1: INSTANCIAR REPOSITÓRIO
        # ====================================================================
        print("Etapa 1: Instanciando ReadingRepository...")
        # O repositório carrega automaticamente variáveis de ambiente e constrói
        # a string de conexão. Nenhuma configuração manual necessária!
        repository = ReadingRepository()
        print("✓ ReadingRepository instanciado com conexão automática")

        # ====================================================================
        # ETAPA 2: BUSCAR ESTAÇÃO EXISTENTE
        # ====================================================================
        print("Etapa 2: Buscando estação...")
        station_id = 1  # Usar ID 1 como exemplo (deve existir no banco)
        station = repository.get_station_by_id(station_id)

        if not station:
            raise ValueError(
                f"Estação com ID {station_id} não encontrada no banco.\n"                
            )

        print(f"✓ Estação encontrada: {station.code} ({station.name})")
        print(f"  Localização: ({station.latitude}, {station.longitude})")

        # ====================================================================
        # ETAPA 3: CRIAR READING VALUES (PARÂMETROS)
        # ====================================================================
        print("Etapa 3: Criando ReadingValue objects...")

        # Parâmetros meteorológicos a serem persistidos
        # Todos os parâmetros devem estar cadastrados em Parameters table
        reading_values = (
            ReadingValue(
                parameter_code="temperature",
                value=Decimal("21.06"),
            ),
            ReadingValue(
                parameter_code="humidity",
                value=Decimal("65.50"),
            ),
            ReadingValue(
                parameter_code="pressure",
                value=Decimal("1013.25"),
            ),
            ReadingValue(
                parameter_code="wind_speed",
                value=Decimal("12.40"),
            ),
        )

        print(f"✓ {len(reading_values)} ReadingValue(s) criados:")
        for rv in reading_values:
            print(f"  - {rv.parameter_code}: {rv.value}")

        # ====================================================================
        # ETAPA 4: CRIAR READING
        # ====================================================================
        print("Etapa 4: Criando objeto Reading...")

        # Usar timestamp atual em UTC (obrigatório timezone-aware)
        timestamp = datetime.now(timezone.utc)

        reading = Reading(
            station_id=station.id,
            timestamp=timestamp,
            values=reading_values,
        )

        print(f"✓ Reading criado:")
        print(f"  - Estação ID: {reading.station_id}")
        print(f"  - Timestamp: {reading.timestamp}")
        print(f"  - Valores: {len(reading.values)}")

        # ====================================================================
        # ETAPA 5: PERSISTIR LEITURA (SAVE)
        # ====================================================================
        print("Etapa 5: Persistindo leitura no banco...")

        reading_id = repository.save(reading)

        print(f"✓ Leitura persistida com sucesso!")
        print(f"  ID da leitura: {reading_id}")

        # ====================================================================
        # ETAPA 6: RECUPERAR DADOS PARA VALIDAR
        # ====================================================================
        print("Etapa 6: Validando dados persistidos...")

        # Recuperar leituras da estação no período de hoje
        start_date = datetime.now(timezone.utc) - timedelta(hours=1)
        end_date = datetime.now(timezone.utc) + timedelta(hours=1)

        recovered_readings = repository.get_by_station(
            station_id=station.id,
            start_date=start_date,
            end_date=end_date,
        )

        if recovered_readings:
            print(f"✓ {len(recovered_readings)} leitura(s) recuperada(s)")

            # Buscar a última leitura (a que acabamos de inserir)
            last_reading = recovered_readings[-1]
            print(f"\nDetalhes da leitura recuperada (ID={reading_id}):")
            print(f"  Timestamp: {last_reading.timestamp}")
            print(f"  Número de valores: {len(last_reading.values)}")
            print("\n  Valores:")

            for value in last_reading.values:
                print(
                    f"    • {value.parameter_code:25} = {value.value:10}"
                )

            print("\n✅ Validação concluída com sucesso!")
            print("   Dados foram persistidos e recuperados corretamente.")

        else:
            print("⚠ Nenhuma leitura foi recuperada para validação.")

    except ValueError as e:
        print(f"❌ Erro de configuração: {e}")
        raise
    except Exception as e:
        print(f"❌ Erro: {e}")
        raise


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Execução falhou: {e}")
        exit(1)
