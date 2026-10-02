# Setup & Installation Guide

## Prerequisites

- **Python 3.14.7** or higher
- **SQL Server** (Express or Developer edition)
- **Git** for version control

## Environment Setup

### 1. Clone Repository

```bash
cd c:\dev\repo\academia_data_science\projeto1
git clone <repo-url> AcademiaDataScience-Projeto1
cd AcademiaDataScience-Projeto1
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Key packages:**
```
pandas==1.5.3
requests==2.31.0
pyodbc==5.0.1
cryptography==41.0.0
streamlit==1.28.1
pytest==7.4.4
pytest-cov==4.1.0
pytest-mock==3.12.0
```

### 4. Configure SQL Server

#### Option A: Local SQL Server Express

**Environment Variables:**
```bash
# .env file or system environment variables
SQL_SERVER=localhost\SQLEXPRESS
SQL_DATABASE=EnvironmentalMonitoring
```

**Create Database:**
```sql
CREATE DATABASE EnvironmentalMonitoring;
USE EnvironmentalMonitoring;
```

Then run SQL scripts:
```bash
# Connect to SQL Server and execute
sql/CREATE_TABLES.sql
sql/POPULATE_DATABASE.sql  # Optional: seed data
```

#### Option B: Remote SQL Server

```bash
SQL_SERVER=<server-address>
SQL_DATABASE=<database-name>
SQL_USER=<username>
SQL_PASSWORD=<password>
```

### 5. Configure API Keys

**Create `src/config.py` section:**
```python
API_KEY_MEERSENS = "your_api_key_here"  # Encrypt antes de commitar!
```

**Security:** Use `src/security/security.py` para encriptar chaves antes do versionamento

## Running the Application

### Web UI (Streamlit)

```bash
cd AcademiaDataScience-Projeto1
python -m streamlit run examples/streamlit_app.py
```

Acesso: `http://localhost:8501`

**Features:**
- Seleção de estação
- Intervalo de datas (máx. 90 dias)
- Ingestão paralela (weather + water)
- Visualização de estatísticas
- Download de CSV

### CLI Pipeline

```bash
python -m src.main --cli
```

**Output:**
- 11 etapas progressivas
- Logging detalhado
- Resultados no terminal

### Padrão (Streamlit)

```bash
python -m src.main
```

## Running Tests

### Quick Test Run

```bash
python tests/run_tests.py
```

### With Coverage Report

```bash
python tests/run_tests.py --coverage
```

Gera: `htmlcov/index.html` (abrir em browser)

### Specific Test Markers

```bash
# Unit tests only
python tests/run_tests.py --unit

# Integration tests
python tests/run_tests.py --integration

# Database tests
python tests/run_tests.py --database

# Analytics tests
python tests/run_tests.py --analytics
```

### Verbose Output

```bash
python tests/run_tests.py --coverage --verbose
```

## Troubleshooting

### "Cannot connect to SQL Server"

1. Verify SQL Server is running
2. Check connection string in environment
3. Test connection:
   ```bash
   python -c "from src.database.reading_repository import ReadingRepository; r = ReadingRepository(); print('Connected!')"
   ```

### "API Key not found"

1. Verify `src/config.py` has chave
2. Verify criptografia está desativada em ambiente dev
3. Check logs: `logs/app.log`

### "Port 8501 already in use"

```bash
streamlit run examples/streamlit_app.py --server.port 8502
```

### Test Failures

Check isolation:
```bash
python tests/run_tests.py --verbose
```

Limpar cache:
```bash
rm -rf .pytest_cache __pycache__ htmlcov .coverage
python tests/run_tests.py --coverage
```

## IDE Setup

### VS Code

**settings.json:**
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black"
}
```

### PyCharm

1. Project → Settings → Python Interpreter
2. Add Interpreter → Existing Environment
3. Select `venv/bin/python`

## Next Steps

- Read [ARCHITECTURE.md](ARCHITECTURE.md) para design
- See [MODULES.md](MODULES.md) para API modules
- Check [API.md](API.md) para endpoints externos
- Visit [tests/README.md](../tests/README.md) para testing
