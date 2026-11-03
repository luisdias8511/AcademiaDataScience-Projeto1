"""Resultado da atualização da camada Gold."""

from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID


@dataclass
class GoldUpdateResult:
    """Resultado da atualização da camada Gold.
    
    Atributos:
        pipeline_run_id: Identificador único da execução.
        start_date: Data inicial do período processado.
        end_date: Data final do período processado.
        started_at: Timestamp de início da execução.
        finished_at: Timestamp de término da execução.
        duration_seconds: Duração total da execução em segundos.
        inserted_dates: Quantidade de datas inseridas em DimDate.
        inserted_times: Quantidade de horários inseridos em DimTime.
        inserted_facts: Quantidade de fatos inseridos em FactMeasurements.
        updated_facts: Quantidade de fatos atualizados em FactMeasurements.
        processed_facts: Total de fatos processados (inseridos + atualizados).
        error_message: Mensagem de erro se houver falha (None se sucesso).
    """
    
    pipeline_run_id: UUID
    start_date: date
    end_date: date
    started_at: datetime
    finished_at: datetime
    duration_seconds: float
    inserted_dates: int
    inserted_times: int
    inserted_facts: int
    updated_facts: int
    processed_facts: int
    error_message: str | None = None
    
    @property
    def is_success(self) -> bool:
        """Indica se a operação foi bem-sucedida."""
        return self.error_message is None
    
    @property
    def total_metrics(self) -> int:
        """Total de registros afetados."""
        return self.inserted_dates + self.inserted_times + self.processed_facts
