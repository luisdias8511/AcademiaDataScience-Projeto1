"""Serviço de atualização da camada Gold do data warehouse."""

import logging
from datetime import date, datetime, timezone, timedelta
from uuid import uuid4
import pyodbc

from src.database.gold_repository import GoldRepository
from src.models.gold_update_result import GoldUpdateResult
from src.config import logger


class GoldUpdateService:
    """Coordena a atualização da camada Gold a partir da camada Silver."""

    def __init__(self, repository: GoldRepository | None = None) -> None:
        """Inicializa o serviço com repositório opcional.
        
        Args:
            repository: Repositório Gold (opcional).
                       Se não fornecido, cria um novo.
        """
        self.repository = repository or GoldRepository()

    def update_gold_layer(
        self,
        start_date: date,
        end_date: date
    ) -> GoldUpdateResult:
        """Atualiza a camada Gold para o período selecionado.
        
        Orquestra todo o processo:
        1. Valida tabelas Gold
        2. Valida dimensões
        3. Insere DimDate
        4. Insere DimTime
        5. Prepara analytics
        6. Faz UPSERT de fatos
        7. Calcula duração
        
        Args:
            start_date: Data inicial do período (inclusiva)
            end_date: Data final do período (inclusiva)
        
        Returns:
            GoldUpdateResult com resumo da operação
        """
        pipeline_run_id = uuid4()
        started_at = datetime.now(timezone.utc).replace(tzinfo=None)
        
        logger.info(
            f"Iniciando atualização Gold | "
            f"PipelineRunId: {pipeline_run_id} | "
            f"Período: {start_date} a {end_date}"
        )
        
        try:
            # Conectar ao banco
            self.repository._connect()
            
            # pyodbc usa transações implícitas por padrão
            # Desabilitar autocommit para manter a transação aberta
            self.repository.conn.autocommit = False
            
            # ================================================================
            # 1. VALIDAR TABELAS GOLD EXISTEM
            # ================================================================
            if not self.repository.validate_gold_tables_exist():
                raise ValueError(
                    "As tabelas da camada Gold não foram encontradas no banco de dados"
                )
            
            # ================================================================
            # 2. VALIDAR DIMENSÕES PARA O PERÍODO
            # ================================================================
            is_valid, error_msg = self.repository.validate_dimensions_for_period(
                start_date,
                end_date
            )
            if not is_valid:
                raise ValueError(
                    error_msg or (
                        "A camada Gold não possui todas as estações ou parâmetros "
                        "necessários para processar o período selecionado"
                    )
                )
            
            # ================================================================
            # 3. VERIFICAR SE HÁ DADOS PARA O PERÍODO
            # ================================================================
            cursor = self.repository.conn.cursor()
            start_dt = datetime.combine(start_date, datetime.min.time())
            end_dt = datetime.combine(end_date + timedelta(days=1), datetime.min.time())
            
            cursor.execute(
                "SELECT COUNT(*) FROM dbo.Readings WHERE DateTime >= ? AND DateTime < ?",
                start_dt,
                end_dt
            )
            reading_count = cursor.fetchone()[0]
            
            if reading_count == 0:
                self.repository.conn.rollback()
                self.repository._disconnect()
                
                finished_at = datetime.now(timezone.utc).replace(tzinfo=None)
                duration = (finished_at - started_at).total_seconds()
                
                logger.warning(
                    f"Nenhuma leitura encontrada para o período {start_date} a {end_date}"
                )
                
                return GoldUpdateResult(
                    pipeline_run_id=pipeline_run_id,
                    start_date=start_date,
                    end_date=end_date,
                    started_at=started_at,
                    finished_at=finished_at,
                    duration_seconds=duration,
                    inserted_dates=0,
                    inserted_times=0,
                    inserted_facts=0,
                    updated_facts=0,
                    processed_facts=0,
                    error_message=(
                        "Não foram encontradas leituras na camada Silver "
                        "para o período selecionado"
                    )
                )
            
            # ================================================================
            # 4. INSERIR DATAS EM DIMDATE
            # ================================================================
            logger.info(f"Inserindo datas em gold.DimDate")
            inserted_dates = self.repository.insert_dim_dates(
                start_date,
                end_date
            )
            logger.info(f"Datas inseridas: {inserted_dates}")
            
            # ================================================================
            # 5. INSERIR HORÁRIOS EM DIMTIME
            # ================================================================
            logger.info(f"Inserindo horários em gold.DimTime")
            inserted_times = self.repository.insert_dim_times(
                start_date,
                end_date
            )
            logger.info(f"Horários inseridos: {inserted_times}")
            
            # ================================================================
            # 6. CRIAR TEMP TABLE COM ANALYTICS
            # ================================================================
            logger.info(f"Preparando cálculos analíticos")
            analytics_count = self.repository.create_fact_analytics_temp_table(
                start_date,
                end_date,
                pipeline_run_id
            )
            logger.info(f"Registros para processamento: {analytics_count}")
            
            # ================================================================
            # 7. FAZER UPSERT DE FATOS
            # ================================================================
            logger.info(f"Atualizando/inserindo fatos")
            inserted_facts, updated_facts = self.repository.upsert_facts()
            logger.info(
                f"Fatos inseridos: {inserted_facts}, "
                f"Fatos atualizados: {updated_facts}"
            )
            
            # ================================================================
            # 8. LIMPAR TEMP TABLE
            # ================================================================
            self.repository.cleanup_temp_table()
            
            # ================================================================
            # 9. CONFIRMAR TRANSAÇÃO
            # ================================================================
            self.repository.conn.commit()
            logger.info(f"Transação confirmada com sucesso")
            
            # ================================================================
            # 10. RETORNAR RESULTADO
            # ================================================================
            finished_at = datetime.now(timezone.utc).replace(tzinfo=None)
            duration = (finished_at - started_at).total_seconds()
            
            logger.info(
                f"Atualização Gold concluída com sucesso | "
                f"Duração: {duration:.2f}s"
            )
            
            return GoldUpdateResult(
                pipeline_run_id=pipeline_run_id,
                start_date=start_date,
                end_date=end_date,
                started_at=started_at,
                finished_at=finished_at,
                duration_seconds=duration,
                inserted_dates=inserted_dates,
                inserted_times=inserted_times,
                inserted_facts=inserted_facts,
                updated_facts=updated_facts,
                processed_facts=inserted_facts + updated_facts
            )
            
        except Exception as e:
            # Fazer rollback em caso de erro
            try:
                self.repository.conn.rollback()
            except:
                pass
            
            error_msg = str(e)
            logger.error(
                f"Erro ao atualizar Gold: {error_msg}",
                exc_info=True
            )
            
            finished_at = datetime.now(timezone.utc).replace(tzinfo=None)
            duration = (finished_at - started_at).total_seconds()
            
            return GoldUpdateResult(
                pipeline_run_id=pipeline_run_id,
                start_date=start_date,
                end_date=end_date,
                started_at=started_at,
                finished_at=finished_at,
                duration_seconds=duration,
                inserted_dates=0,
                inserted_times=0,
                inserted_facts=0,
                updated_facts=0,
                processed_facts=0,
                error_message=(
                    "Não foi possível atualizar a camada Gold. "
                    "Consulte os logs para obter mais informações"
                )
            )
        
        finally:
            try:
                if self.repository.conn:
                    self.repository.conn.autocommit = True
            except:
                pass
            self.repository._disconnect()
