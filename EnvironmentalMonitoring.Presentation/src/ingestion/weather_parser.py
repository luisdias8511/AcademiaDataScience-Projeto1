"""Parser para dados meteorológicos da API."""

from datetime import datetime, timezone
from decimal import Decimal

from src.constants import CATEGORY_WEATHER
from src.database.reading_repository import ReadingRepository
from src.models.reading import Reading
from src.models.reading_value import ReadingValue


class WeatherParser:
    """Transforma dados brutos da API meteorológica em objetos Reading.
    
    Responsabilidades:
    - Mapear CodeApi (temperature, humidity, etc.) para Code interno
    - Validar dados recebidos da API
    - Construir objetos Reading com ReadingValue corretamente tipados
    
    A implementação é genérica: funciona para qualquer parâmetro existente
    na tabela Parameters, sem hardcoding específico para campos individuais.
    """

    def __init__(self, repository: ReadingRepository) -> None:
        """Inicializa parser com repositório para consultas de parâmetros.
        
        Args:
            repository: ReadingRepository para acessar configuração de parâmetros.
        """
        self.repository = repository

    def parse(
        self,
        station_id: int,
        api_payload: dict,
    ) -> list[Reading]:
        """Transforma dados da API meteorológica em lista de objetos Reading.
        
        Args:
            station_id: ID da estação meteorológica.
            api_payload: Resposta JSON da API (com chave "values").
        
        Returns:
            Lista de Reading, um para cada timestamp encontrado.
        
        Raises:
            ValueError: Se payload está vazio ou malformado.
            KeyError: Se estrutura esperada não existe.
        """
        if not api_payload:
            raise ValueError("Payload da API não pode estar vazio.")

        # Extrair lista de valores do payload
        values_list = api_payload.get("values")
        if values_list is None:
            raise KeyError("Chave 'values' não encontrada no payload da API.")

        if not isinstance(values_list, list):
            raise TypeError("A chave 'values' deve ser uma lista.")

        readings: list[Reading] = []

        # Processar cada medição individual
        for value_entry in values_list:
            reading = self._parse_single_entry(station_id, value_entry)
            if reading and reading.values:  # Apenas adicionar se houver valores
                readings.append(reading)

        return readings

    def _parse_single_entry(
        self,
        station_id: int,
        entry: dict,
    ) -> Reading | None:
        """Transforma uma entrada individual em Reading.
        
        Args:
            station_id: ID da estação.
            entry: Dicionário com uma medição (contém datetime e parâmetros).
        
        Returns:
            Reading com ReadingValue para cada parâmetro válido, ou None se vazio.
        """
        if not entry or not isinstance(entry, dict):
            return None

        # Extrair timestamp
        timestamp_str = entry.get("datetime")
        if not timestamp_str:
            return None

        try:
            # Parser ISO 8601 com suporte a timezone
            # Se não tem timezone, assume UTC
            if "+" in timestamp_str or timestamp_str.endswith("Z"):
                # ISO com timezone
                timestamp = datetime.fromisoformat(
                    timestamp_str.replace("Z", "+00:00")
                )
            else:
                # ISO sem timezone - assume UTC
                timestamp = datetime.fromisoformat(timestamp_str).replace(
                    tzinfo=timezone.utc
                )

            # Garantir que está em UTC
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=timezone.utc)
            else:
                timestamp = timestamp.astimezone(timezone.utc)

        except (ValueError, TypeError) as e:
            return None

        # Extrair parâmetros - genérico para qualquer chave
        reading_values: list[ReadingValue] = []

        for key, value in entry.items():
            # Pular campos estruturais (não são parâmetros)
            if key in {"datetime", "name", "shortcode", "network", "found", "confidence", "index"}:
                continue

            # Pular valores None
            if value is None:
                continue

            # Tenta interpretar como parâmetro
            reading_value = self._parse_parameter_value(key, value)
            if reading_value:
                reading_values.append(reading_value)

        # Retornar Reading apenas se houver parâmetros válidos
        if not reading_values:
            return None

        return Reading(
            station_id=station_id,
            timestamp=timestamp,
            values=tuple(reading_values),
        )

    def _parse_parameter_value(
        self,
        api_field: str,
        api_value,
    ) -> ReadingValue | None:
        """Transforma um campo da API em ReadingValue.
        
        Args:
            api_field: Nome do campo da API (ex: "temperature", "humidity").
            api_value: Valor do campo.
        
        Returns:
            ReadingValue com parameter_code interno, ou None se não encontrado.
        """
        if api_value is None:
            return None

        try:
            # Tentar converter para float para validação
            float_value = float(api_value)

            # Consultar banco para mapear api_field para Parameter
            parameter = self.repository.get_parameter_by_api_code(
                code_api=api_field,
                category_code=CATEGORY_WEATHER,
            )

            # Se parâmetro não existir no banco, ignora silenciosamente
            if not parameter:
                return None

            # Criar ReadingValue com code interno
            return ReadingValue(
                parameter_code=parameter.code,
                value=Decimal(str(float_value)),
            )

        except (ValueError, TypeError):
            # Valor não é numérico, ignora
            return None
