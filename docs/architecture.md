# System Architecture

## Overview

```
┌─────────────────┐
│  External APIs  │
│ Meersens Water  │
│ Meersens Weather│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  ETL Pipeline   │  src/ingestion/
│ • Fetch & Parse │  • etl_water.py
│ • Validate      │  • etl_weather.py
│ • Normalize     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  SQL Server DB  │  src/database/
│ • Stations      │  reading_repository.py
│ • Readings      │
│ • Parameters    │
│ • ReadingValues │
└────────┬────────┘
         │
    ┌────┴────┬──────────┐
    ▼         ▼          ▼
┌────────┐ ┌──────┐ ┌─────────┐
│Analytics│ │ CSV  │ │Streamlit│
│Service  │ │Export│ │   UI    │
└────────┘ └──────┘ └─────────┘
```

## Core Components

### 1. Ingestion (src/ingestion/)
- **etl_water.py** (100% coverage)
  - Fetch from Meersens Water API
  - Parse JSON, normalize data
  - Caching de parâmetros (evita redundância)
  - Pagination com detecção de duplicatas via MD5

- **etl_weather.py** (96% coverage)
  - Fetch from Meersens Weather API
  - Same structure como water module
  - Extração de 8+ parâmetros meteorológicos

### 2. Data Models (src/models/)
- **Station**: Estação (id, code, name, lat, lng)
- **Reading**: Leitura temporal (station_id, timestamp, values[])
- **ReadingValue**: Valor medido (parameter_code, value)
- **Parameter**: Metadados (code, name, unit, category_id)
- **StatisticsResult**: Resultado análise (media, mediana, outliers, etc)

### 3. Database Layer (src/database/)
- **ReadingRepository**: DAO pattern
  - CRUD para Readings
  - Queries para estatísticas
  - Busca de parâmetros (fetch names para UI)
  - Connection pooling com pyodbc

### 4. Analytics (src/analytics/)
- **AnalyticsService**: Calcula por parâmetro
  - Tendência central (média, mediana)
  - Dispersão (desvio padrão, IQR)
  - Outliers via regra IQR (1.5 × IQR)
  - Enriquecimento com nomes de parâmetros

### 5. Reporting (src/reporting/)
- **CSV Export**: Estatísticas + Outliers
- Formatação automática

### 6. Security (src/security/)
- **Encryption**: AES-256 para API keys
- **Logging**: Auditoria com traceability
- Sanitização de URLs em logs

## Data Flow

### Ingestão
```
API → Fetch (requests) → Parse (pandas) → Normalize → Validate → Store
```

### Análise
```
DB → Load Readings → Group by Parameter → Calculate Stats → Enrich Names
```

### Visualização
```
UI (Streamlit) → Run Pipeline → Show Stats → Export CSV
```

## Technology Stack

| Layer | Technology |
|-------|-----------|
| **Language** | Python 3.14.7 |
| **Data** | pandas, Decimal |
| **Database** | SQL Server (pyodbc) |
| **APIs** | requests |
| **UI** | Streamlit |
| **Testing** | pytest (286+ tests, 58% coverage) |
| **Security** | cryptography, logging |

## Design Patterns

1. **Repository Pattern**: ReadingRepository encapsula acesso a dados
2. **Service Layer**: AnalyticsService, IngestionService lógica separada
3. **Value Objects**: Parameter, Reading, StatisticsResult (imutáveis)
4. **Dependency Injection**: Services recebem repositório opcional
5. **ETL Pipeline**: Validação → Transformação → Persistência

## Key Features

### Robustness
- Tratamento de exceções em todos os níveis
- Retry logic em APIs
- Connection pooling
- Validação de dados

### Performance
- Parallel ingestion (ThreadPoolExecutor)
- Caching de metadados
- Batch operations
- Query optimization com indexes

### Maintainability
- Type hints (type-safe)
- Frozen dataclasses (immutable)
- Comprehensive logging
- 286+ unit + integration tests
- Clean code principles
