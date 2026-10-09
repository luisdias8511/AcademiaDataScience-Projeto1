"""Serviço de negócios para consultas históricas."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from math import ceil

from src.database.history_repository import HistoryRepository
from src.exceptions import (
    InvalidDateRangeError,
    StationNotFoundError,
    UnsupportedUnitSystemError,
)
from src.models.database_models import ParameterValueRecord, ReadingRecord, Station
from src.schemas.common import PageResponse, ParameterValueResponse
from src.schemas.water import WaterEntryResponse, WaterHistoryResponse
from src.schemas.weather import WeatherEntryResponse, WeatherHistoryResponse

MAX_PAGE_SIZE = 500
CATEGORY_WEATHER = "WEATHER"
CATEGORY_WATER = "WATER"


class HistoryService:
    """Orquestra consultas ao repositório de histórico."""

    def __init__(self, repository: HistoryRepository | None = None) -> None:
        """Inicializa serviço com repositório simples."""
        self.repository = repository or HistoryRepository()

    def list_top_stations(self, limit: int = 10) -> list[Station]:
        """Lista estações para uso inicial da API."""
        return self.repository.get_top_stations(limit=limit)

    def get_weather_history(
        self,
        latitude: Decimal,
        longitude: Decimal,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        page: int = 0,
        system: str = "metric",
    ) -> WeatherHistoryResponse:
        """Retorna histórico meteorológico em formato compatível com contrato esperado."""
        if system != "metric":
            raise UnsupportedUnitSystemError(
                "O parâmetro 'system' suporta apenas o valor 'metric'."
            )

        _, _, start_db, end_db = self._resolve_date_interval(from_date, to_date)
        station = self.repository.get_station_by_coordinates(latitude, longitude)
        if station is None:
            raise StationNotFoundError("Localização não encontrada.")

        records, total_elements = self.repository.get_history(
            station_id=station.id,
            category_code=CATEGORY_WEATHER,
            start_date=start_db,
            end_date=end_db,
            page=page,
            page_size=MAX_PAGE_SIZE,
        )

        values = [self._to_weather_entry(record) for record in records]
        page_info = self._build_page_response(total_elements=total_elements, page_number=page)
        return WeatherHistoryResponse(
            found=len(values) > 0,
            values=values,
            page=page_info,
        )

    def get_water_history(
        self,
        latitude: Decimal,
        longitude: Decimal,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        page: int = 0,
    ) -> WaterHistoryResponse:
        """Retorna histórico hídrico em formato compatível com contrato esperado."""
        _, _, start_db, end_db = self._resolve_date_interval(from_date, to_date)
        station = self.repository.get_station_by_coordinates(latitude, longitude)
        if station is None:
            raise StationNotFoundError("Localização não encontrada.")

        records, total_elements = self.repository.get_history(
            station_id=station.id,
            category_code=CATEGORY_WATER,
            start_date=start_db,
            end_date=end_db,
            page=page,
            page_size=MAX_PAGE_SIZE,
        )

        values = [self._to_water_entry(record) for record in records]
        page_info = self._build_page_response(total_elements=total_elements, page_number=page)
        return WaterHistoryResponse(
            found=len(values) > 0,
            values=values,
            page=page_info,
        )

    def _resolve_date_interval(
        self,
        from_date: datetime | None,
        to_date: datetime | None,
    ) -> tuple[datetime, datetime, datetime, datetime]:
        """Resolve datas opcionais, normaliza para UTC e prepara valores para o SQL."""
        to_utc = self._normalize_utc(to_date) if to_date else self._current_utc_hour_start()
        from_utc = (
            self._normalize_utc(from_date) if from_date else (to_utc - timedelta(hours=24))
        )

        if from_utc >= to_utc:
            raise InvalidDateRangeError("Intervalo inválido: 'from' deve ser menor que 'to'.")

        start_db = from_utc.replace(tzinfo=None)
        end_db = to_utc.replace(tzinfo=None)
        return from_utc, to_utc, start_db, end_db

    @staticmethod
    def _normalize_utc(value: datetime) -> datetime:
        """Normaliza datetime para UTC (datas sem fuso são tratadas como UTC)."""
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    @staticmethod
    def _current_utc_hour_start() -> datetime:
        """Retorna início da hora atual em UTC."""
        now_utc = datetime.now(timezone.utc)
        return now_utc.replace(minute=0, second=0, microsecond=0)

    @staticmethod
    def _build_page_response(total_elements: int, page_number: int) -> PageResponse:
        """Monta metadados de paginação."""
        total_pages = ceil(total_elements / MAX_PAGE_SIZE) if total_elements > 0 else 0
        return PageResponse(
            totalElements=total_elements,
            totalPages=total_pages,
            pageNumber=page_number,
            size=MAX_PAGE_SIZE,
        )

    def _to_weather_entry(self, record: ReadingRecord) -> WeatherEntryResponse:
        """Converte leitura interna para entrada de resposta meteorológica."""
        parameters: dict[str, ParameterValueResponse] = {}
        for value in record.values:
            parameters[value.code_api] = self._to_parameter_value_response(value)

        return WeatherEntryResponse(
            found=len(parameters) > 0,
            datetime=self._format_datetime_utc(record.timestamp),
            index=None,
            parameters=parameters,
        )

    def _to_water_entry(self, record: ReadingRecord) -> WaterEntryResponse:
        """Converte leitura interna para entrada de resposta hídrica."""
        pollutants: dict[str, ParameterValueResponse] = {}
        for value in record.values:
            pollutants[value.code_api] = self._to_parameter_value_response(value)

        return WaterEntryResponse(
            found=len(pollutants) > 0,
            datetime=self._format_datetime_utc(record.timestamp),
            index=None,
            pollutants=pollutants,
        )

    @staticmethod
    def _to_parameter_value_response(value: ParameterValueRecord) -> ParameterValueResponse:
        """Converte valor interno para schema de parâmetro da API."""
        return ParameterValueResponse(
            shortcode=None,
            name=value.name,
            unit=value.unit,
            found=True,
            value=value.value,
            confidence=None,
            index=None,
        )

    @staticmethod
    def _format_datetime_utc(value: datetime) -> str:
        """Formata datetime para padrão UTC fixo esperado pela API."""
        if value.tzinfo is None:
            utc_value = value.replace(tzinfo=timezone.utc)
        else:
            utc_value = value.astimezone(timezone.utc)
        return utc_value.strftime("%Y-%m-%dT%H:%M:%S.000Z")
