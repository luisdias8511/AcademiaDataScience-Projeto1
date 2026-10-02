# Module Reference

## Directory Structure

```
src/
├── __init__.py
├── main.py                      # Pipeline orquestrador
├── config.py                    # Configurações globais
├── constants.py                 # Constantes do app
├── analytics/
│   ├── __init__.py
│   ├── service.py              # AnalyticsService
│   └── statistics.py           # Cálculos estatísticos
├── database/
│   ├── __init__.py
│   └── reading_repository.py   # ReadingRepository (DAO)
├── ingestion/
│   ├── __init__.py
│   ├── etl_water.py            # Water ETL (100% coverage)
│   ├── etl_weather.py          # Weather ETL (96% coverage)
│   └── service.py              # IngestionService
├── models/
│   ├── __init__.py
│   ├── parameter.py            # Parameter model
│   ├── reading.py              # Reading model
│   ├── reading_value.py        # ReadingValue model
│   ├── station.py              # Station model
│   └── statistics_result.py    # StatisticsResult model
├── processing/
│   ├── __init__.py
│   └── reading_processor.py    # Processamento de dados
├── reporting/
│   ├── __init__.py
│   └── csv_export.py           # CSV export
├── security/
│   ├── __init__.py
│   ├── security.py             # Criptografia AES-256
│   └── log_utils.py            # Logging com auditoria
└── presentation/
    ├── __init__.py
    └── streamlit_support.py    # Funções Streamlit UI
```

## Core Models

### Station
```python
@dataclass(frozen=True, slots=True)
class Station:
    id: int | None
    code: str                      # Código único (ex: "EST001")
    name: str                      # Nome descritivo
    latitude: float                # Coordenada
    longitude: float               # Coordenada
```

### Reading
```python
@dataclass(frozen=True, slots=True)
class Reading:
    station_id: int                # FK to Station
    timestamp: datetime            # UTC-aware
    values: tuple[ReadingValue, ...]
```

### ReadingValue
```python
@dataclass(frozen=True, slots=True)
class ReadingValue:
    parameter_code: str            # Ex: "TEMPERATURE"
    value: Decimal                 # Precisão decimal
```

### Parameter
```python
@dataclass(frozen=True, slots=True)
class Parameter:
    id: int | None
    code: str                      # Código interno (ex: "TEMPERATURE")
    code_api: str                  # Código API (ex: "temperature")
    name: str                      # Nome exibição (ex: "Temperatura")
    unit: str | None               # Ex: "°C"
    category_id: int               # 1=Weather, 2=Water
```

### StatisticsResult
```python
@dataclass(frozen=True, slots=True)
class StatisticsResult:
    parameter_code: str
    parameter_name: str | None    # Enriquecido pelo BD
    count: int
    average: float
    median: float
    standard_deviation: float
    q1: float                      # 25º percentil
    q3: float                      # 75º percentil
    iqr: float                     # Q3 - Q1
    lower_bound: float             # Q1 - 1.5*IQR (outlier threshold)
    upper_bound: float             # Q3 + 1.5*IQR
    outliers: tuple[float, ...]    # Valores identificados como outliers
```

## Services

### AnalyticsService
```python
class AnalyticsService:
    def __init__(self, repository: ReadingRepository | None = None)
    def calculate(self, readings: list[Reading]) -> list[StatisticsResult]
```

**Funcionalidades:**
- Agrupa readings por parameter_code
- Calcula tendência central, dispersão
- Identifica outliers via IQR
- Enriquece com nomes de parâmetros (se repositório fornecido)
- Validação: mínimo 2 observações por parâmetro

### IngestionService
```python
class IngestionService:
    def fetch_weather_readings(
        station: Station,
        start_date: datetime,
        end_date: datetime
    ) -> list[Reading]
    
    def get_water_readings(
        station: Station,
        start_date: datetime,
        end_date: datetime
    ) -> list[Reading]
```

**Funcionalidades:**
- Busca dados de APIs (Meersens)
- Normaliza JSON para modelos
- Detecção de duplicatas (MD5)
- Caching de parâmetros
- Tratamento de erros com retry

### ReadingRepository
```python
class ReadingRepository:
    def save(self, reading: Reading, parameter_category_id: int) -> int
    def save_many(self, readings: list[Reading], category_id: int) -> list[int]
    def get_by_station(
        self, station_id: int, 
        start_date: datetime, end_date: datetime,
        parameter_category_id: int
    ) -> list[Reading]
    def get_parameter_by_code(self, parameter_code: str) -> Parameter | None
    def get_stations() -> list[Station]
```

**Operações:**
- CRUD para Readings
- Batch operations (save_many)
- Queries com filtros
- Busca de metadados (Parameters, Stations)
- Connection management

## ETL Modules

### etl_water.py
```python
def consulta_api(
    lat: float, lng: float,
    from_date: datetime, to_date: datetime
) -> list[Reading]
```

**Pipeline:**
1. `_fetch_water_history()` - requests.get() com headers
2. `_normalize_water_data()` - pd.json_normalize()
3. `_extract_parameter_columns()` - Filtra colunas conhecidas
4. Validação e conversão de tipos
5. Retorna lista de Reading objects

**Características:**
- Pagination automática
- Detecção de duplicatas com MD5 hash
- Caching de parameter codes (evita roundtrips)
- 100% coverage

### etl_weather.py
Estrutura idêntica a etl_water.py
- Mesmo pipeline de fetch → normalize → extract
- Parâmetros diferentes (temperature, humidity, etc)
- 96% coverage (3 linhas faltando em edge cases)

## Database Layer

### SQL Schema
```sql
STATIONS
├─ Id (PK)
├─ Code (UNIQUE)
├─ Name
├─ Latitude
└─ Longitude

PARAMETERS
├─ Id (PK)
├─ Code (UNIQUE)
├─ CodeApi
├─ Name
├─ Unit
└─ CategoryId (FK)

READINGS
├─ Id (PK)
├─ StationId (FK)
└─ DateTime

READINGVALUES
├─ Id (PK)
├─ ReadingId (FK)
├─ ParameterId (FK)
└─ Value
```

## Reporting

### CSV Export
```python
def export_statistics_to_csv(
    statistics: list[StatisticsResult],
    category: str  # "weather" or "water"
) -> str:  # Returns file path
```

**Output columns:**
- Parameter, Count, Average, Median
- StdDev, Q1, Q3, IQR
- Lower/Upper Bounds
- Outlier Count

## Security

### Encryption
```python
from src.security.security import encryptar_api_key, descriptografar_api_key

encrypted = encryptar_api_key("my_secret_key")
decrypted = descriptografar_api_key(encrypted)
```

### Logging
```python
from src.security.log_utils import tratar_erro, log_info

tratar_erro(exception, "contexto", encerrar=False)
```

Logs: `logs/app.log` com auditoria completa

## Streamlit UI

### Key Functions

```python
def statistics_to_rows(
    statistics: list[StatisticsResult]
) -> list[dict]  # Formatado para tabela

def run_pipeline(
    station: Station,
    start_date: date,
    end_date: date
) -> bool  # Executa 11 etapas

def validate_date_range(
    start_date: date,
    end_date: date
) -> str | None  # Retorna erro ou None se válido
```

## Dependencies

```
pandas          # DataFrames
requests        # HTTP calls
pyodbc          # SQL Server
cryptography    # AES-256
streamlit       # UI
```

**Development:**
```
pytest          # Testing
pytest-cov      # Coverage
pytest-mock     # Mocking
pytest-timeout  # Timeouts
```
