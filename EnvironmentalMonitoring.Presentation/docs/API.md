# External APIs Integration

## Overview

Aplicação integra com Meersens API para dados ambientais:
- **Water Quality**: Monitoramento de poluentes na água
- **Weather**: Dados meteorológicos

## Meersens API

### Base URL
```
https://api.meersens.com/environment/public
```

### Authentication
- **Header**: `Authorization: Bearer <API_KEY>`
- **Location**: Store encrypted in `src/config.py`
- **Security**: Descriptografar em runtime via `security.py`

## Weather Endpoint

### Request
```bash
GET /weather/history
Parameters:
  - latitude: float
  - longitude: float
  - from_date: ISO8601 (YYYY-MM-DDTHH:mm:ssZ)
  - to_date: ISO8601
  - page: int (default: 1)
  - page_size: int (default: 100)
```

### Response Example
```json
{
  "location": {
    "latitude": 48.8566,
    "longitude": 2.3522
  },
  "data": [
    {
      "timestamp": "2026-10-02T10:00:00Z",
      "parameters": {
        "temperature": {
          "name": "Temperature",
          "value": 21.06,
          "unit": "°C"
        },
        "humidity": {
          "name": "Humidity",
          "value": 64.37,
          "unit": "%"
        },
        "pressure": {
          "name": "Pressure",
          "value": 972.82,
          "unit": "hPa"
        },
        "wind_speed": {
          "name": "Wind speed",
          "value": 8.99,
          "unit": "km/h"
        },
        "wind_direction": {
          "name": "Wind direction",
          "value": 252.99,
          "unit": "°"
        },
        "cloud_cover": {
          "name": "Cloud cover",
          "value": 97,
          "unit": "%"
        },
        "apparent_temperature": {
          "name": "Apparent temperature",
          "value": 19.5,
          "unit": "°C"
        },
        "precipitations": {
          "name": "Precipitations",
          "value": 0.0,
          "unit": "mm"
        }
      }
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 100,
    "total_pages": 4,
    "total_records": 340
  }
}
```

**Parameters Extracted:**
- Temperature (°C)
- Humidity (%)
- Pressure (hPa)
- Wind Speed (km/h)
- Wind Direction (°)
- Cloud Cover (%)
- Apparent Temperature (°C)
- Precipitations (mm)

## Water Endpoint

### Request
```bash
GET /water/history
Parameters: Same as weather
```

### Response Example
```json
{
  "location": { ... },
  "data": [
    {
      "timestamp": "2026-10-02T10:00:00Z",
      "pollutants": {
        "acenaphthene": { "value": 0.1, "unit": "µg/L" },
        "acrolein": { "value": 0.05, "unit": "µg/L" },
        "benzene": { "value": 1.2, "unit": "µg/L" },
        "nitrate": { "value": 45.0, "unit": "mg/L" },
        "dissolved_oxygen": { "value": 8.5, "unit": "mg/L" },
        "ph": { "value": 7.2, "unit": "" },
        "temperature": { "value": 18.5, "unit": "°C" },
        "turbidity": { "value": 2.3, "unit": "NTU" },
        "tds": { "value": 450.0, "unit": "mg/L" },
        "ammonia": { "value": 0.3, "unit": "mg/L" },
        "phosphate": { "value": 0.2, "unit": "mg/L" },
        "nitrite": { "value": 0.05, "unit": "mg/L" }
      }
    }
  ],
  "pagination": { ... }
}
```

**Parameters Extracted:**
- Acenaphthene, Acrolein, Benzene
- Nitrate, Nitrite, Ammonia, Phosphate
- Dissolved Oxygen, pH
- Temperature, Turbidity, TDS
- 40+ parâmetros de qualidade da água

## ETL Processing

### Flow

```
1. API Request
   └─ Meersens HTTP call
   └─ Retry logic (3 attempts)
   └─ Timeout: 30s

2. Response Parsing
   └─ pd.json_normalize()
   └─ Extract parameters from nested JSON
   └─ Flatten structure

3. Normalization
   └─ Validate presence of required fields
   └─ Convert types (float, datetime)
   └─ Handle missing values

4. Deduplication
   └─ MD5 hash of (timestamp, station, parameters)
   └─ Skip if already processed
   └─ Pagination aware

5. Persistence
   └─ Create Reading object
   └─ Create ReadingValue objects
   └─ Batch insert to DB
```

### Code Example

```python
from src.ingestion.etl_weather import consulta_api
from datetime import datetime, timezone

# Fetch weather data
readings = consulta_api(
    lat=48.8566,
    lng=2.3522,
    from_date=datetime(2026, 10, 1, tzinfo=timezone.utc),
    to_date=datetime(2026, 10, 2, tzinfo=timezone.utc)
)

print(f"Fetched {len(readings)} readings")
for reading in readings:
    print(f"  {reading.timestamp}: {len(reading.values)} parameters")
```

## Error Handling

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| 401 Unauthorized | Invalid API key | Regenerate and encrypt |
| 429 Rate Limited | Too many requests | Implement backoff |
| 500 Server Error | API down | Retry with exponential backoff |
| Timeout | Slow connection | Increase timeout, check network |
| 404 Not Found | Invalid location | Verify coordinates |

### Retry Strategy

```python
# Automatic retry (3 attempts)
# Exponential backoff: 1s, 2s, 4s
# Timeout per attempt: 30s
```

## Rate Limits

- **Requests/minute**: 60 (check with API)
- **Concurrent**: 5 max recommended
- **Data retention**: 90 days

## Testing

### Mock Responses

```python
from unittest.mock import patch, MagicMock

with patch('requests.get') as mock_get:
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "data": [{"timestamp": "...", "parameters": {...}}],
        "pagination": {"total_pages": 1}
    }
    mock_get.return_value = mock_response
    
    # Call ETL function
    readings = consulta_api(...)
```

## Integration Tests

**Location**: `tests/test_etl.py` (35 tests, 100% coverage)

**Coverage:**
- Fetch with pagination
- Data normalization
- Parameter extraction
- Deduplication
- Error scenarios
- Type conversion

## Performance

### Benchmarks

- Weather fetch: ~8-10s (4 pages × 100 records)
- Water fetch: ~2-3s (4 pages × 100 records)
- Normalization: <1s
- DB persist: 1-2s (batch insert)

### Optimization Tips

1. Use **parallel execution** (ThreadPoolExecutor)
2. **Cache** parameter codes in memory
3. **Batch** operations (save_many)
4. **Paginate** requests (max 100/page)
5. Limit date **range** (90 days recommended)

## Documentation

- Meersens API: https://partners.meersens.com/
- Weather params: See etl_weather.py
- Water params: See etl_water.py
- DB schema: sql/CREATE_TABLES.sql
