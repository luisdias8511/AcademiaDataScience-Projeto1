# 🧪 Suite de Testes - Environmental Monitoring

Este diretório contém todos os testes automatizados para o projeto Environmental Monitoring.

## 📊 Visão Geral

- **272 testes** automatizados
- **58% cobertura** de código
- **3 segundos** tempo de execução
- **11 módulos** de teste

## 🚀 Quick Start

### Instalar dependências de teste
```bash
pip install -r ../requirements-test.txt
```

### Executar todos os testes
```bash
python -m pytest
```

### Executar com cobertura
```bash
python -m pytest --cov=src --cov-report=html
# Abrir htmlcov/index.html no navegador
```

### Executar testes específicos
```bash
python -m pytest tests/test_models.py -v
python -m pytest tests/test_database.py::TestReadingRepository -v
python -m pytest -k "test_save" -v
```

## 📁 Estrutura de Arquivos

```
tests/
├── README.md                    ← Você está aqui
├── run_tests.py               ← Script helper para executar testes
├── conftest.py                ← Fixtures compartilhadas
├── test_models.py             ← Testes de modelos de domínio
├── test_database.py           ← Testes de persistência
├── test_analytics.py          ← Testes de analytics
├── test_ingestion.py          ← Testes de clientes API
├── test_etl.py                ← Testes de ETL (water/weather)
├── test_main.py               ← Testes do pipeline principal
├── test_processing.py         ← Testes de processamento
├── test_reporting.py          ← Testes de relatórios
├── test_security.py           ← Testes de segurança
├── test_integration.py        ← Testes end-to-end
├── test_edge_cases.py         ← Testes de casos extremos
└── test_project_structure.py  ← Validação de estrutura
```

## 📖 Usando o Script Helper

O arquivo `run_tests.py` oferece uma interface conveniente:

```bash
# Executar todos os testes com cobertura
python run_tests.py --coverage

# Apenas testes unitários
python run_tests.py --unit

# Apenas testes de integração
python run_tests.py --integration

# Apenas testes de database
python run_tests.py --database

# Teste específico
python run_tests.py --test tests/test_models.py

# Verbose mode
python run_tests.py -vv

# Com cobertura + verbose
python run_tests.py --coverage -vv
```

## 🏷️ Marcadores (Markers)

Todos os testes estão marcados com categorias:

```bash
# Executar por marcador
pytest -m unit              # Testes unitários
pytest -m integration       # Testes de integração
pytest -m database          # Testes com banco de dados
pytest -m analytics         # Testes de análise
pytest -m security          # Testes de segurança
pytest -m models            # Testes de modelos
```

## 🔧 Configuração

A configuração dos testes está em `../pytest.ini`:

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
python_classes = Test*
addopts = -v --strict-markers --tb=short
```

## 📊 Cobertura

Após executar testes com `--cov`, gerar relatório HTML:

```bash
pytest --cov=src --cov-report=html
```

Abrir `htmlcov/index.html` para ver:
- Cobertura geral do projeto
- Cobertura por módulo
- Linhas cobertas/não cobertas
- Relatório detalhado

### Metas de Cobertura

| Módulo | Meta | Atual | Status |
|--------|------|-------|--------|
| models/ | 100% | 100% | ✅ |
| analytics/ | 90% | 90%+ | ✅ |
| database/ | 70% | 71% | ✅ |
| ingestion/ | 70% | 60-82% | 🟡 |
| processing/ | 60% | 48% | 🟡 |

## 🐛 Fixtures Compartilhadas

Definidas em `conftest.py`:

```python
@pytest.fixture
def sample_station():
    """Estação de teste padrão."""
    return Station(
        id=1,
        code="EST001",
        name="Estação Teste",
        latitude=-15.5,
        longitude=-48.5,
    )

@pytest.fixture
def sample_readings():
    """Lista de leituras de teste."""
    return [...]
```

Usar em qualquer teste:
```python
def test_example(sample_station, sample_readings):
    # Usar fixtures
    assert sample_station.id == 1
```

## 🎯 Dicas de Teste

### Testar função específica
```bash
pytest tests/test_models.py::TestStation::test_station_creation -v
```

### Testar com padrão no nome
```bash
pytest -k "temperature" -v
```

### Testar e parar no primeiro erro
```bash
pytest -x
```

### Testar mostrando N linhas mais lentas
```bash
pytest --durations=10
```

### Testar com saída simplificada
```bash
pytest -q
```

### Testar e pular testes marcados como slow
```bash
pytest -m "not slow"
```

## 📝 Escrevendo Novos Testes

Template padrão:

```python
"""Testes para [component]."""

import pytest
from unittest.mock import Mock, patch
from src.module import Component

class TestComponent:
    """Testes para Component."""
    
    def test_component_behavior(self, sample_fixture):
        """Deve fazer algo específico."""
        # Arrange
        expected = "resultado"
        
        # Act
        result = Component(sample_fixture).method()
        
        # Assert
        assert result == expected
    
    def test_component_error_handling(self):
        """Deve tratar erro corretamente."""
        with pytest.raises(ValueError):
            Component(invalid_input)
```

### Boas Práticas

1. **Uma asserção por teste** (quando possível)
2. **Nomenclatura clara**: `test_xxx_should_yyy_when_zzz`
3. **Arrange-Act-Assert**: Preparar → Executar → Validar
4. **Use fixtures** para setup compartilhado
5. **Mock dependências externas** (APIs, BD)
6. **Teste casos de erro** também

## 🔍 Debug

### Rodar com saída de print
```bash
pytest -s tests/test_models.py
```

### Rodar com debugger (pdb)
```bash
pytest --pdb tests/test_models.py
```

### Rodar apenas um teste com debug
```bash
pytest -s --pdb tests/test_models.py::TestStation::test_creation
```

## 📈 CI/CD

Para integração contínua, usar:

```bash
# Verificar antes de commit
pytest --cov=src -q

# Fazer deploy apenas se passar
pytest --cov=src && git push
```

## 🎓 Aprendizado

- Leia `conftest.py` para entender fixtures
- Veja `test_models.py` para padrão simples
- Veja `test_database.py` para mocking avançado
- Veja `test_integration.py` para end-to-end

## 📚 Documentação

- [pytest docs](https://docs.pytest.org/)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- Ver [TESTS_SUMMARY.md](../docs/TESTS_SUMMARY.md) para detalhes completos

## 🤝 Contribuindo

1. Escrever testes para novo código
2. Executar `pytest --cov=src --cov-report=html`
3. Verificar cobertura > 50%
4. Fazer commit com testes passando

---

**Última Atualização:** 2026-10-02  
**Status:** ✅ 272 testes, 58% cobertura

### 4. **test_reporting.py** - Testes de Exportação
- **TestCSVExport**: Exportação de estatísticas
  - Criação de arquivo
  - Conteúdo correto (cabeçalhos, dados)
  - Formatação decimal (.2f)
  - Localização (pasta results)
  - Nomes únicos (por categoria e timestamp)

- **TestOutliersDetailExport**: Exportação de detalhes de outliers
  - Listagem por linha
  - Suporte a múltiplos parâmetros
  - Casos sem outliers

**Cobertura:** 17 testes para validação de exportação em CSV

---

### 5. **test_database.py** - Testes de Persistência (com Mocks)
- **TestReadingRepository**: Operações de banco de dados
  - `get_stations()`: Retorna lista de Station
  - `save_many()`: Persiste leituras com transação
  - `get_by_station()`: Filtra por estação, data e categoria
  - Tratamento de erros (rollback)
  - Segurança (SQL injection prevention)

**Cobertura:** 17 testes com mocks de conexão pyodbc

---

### 6. **test_security.py** - Testes de Segurança e Logging
- **TestErrorHandling**: Tratamento de erros
  - Logging de mensagens
  - Opção encerrar (SystemExit)
  - Preservação de informações
  - Múltiplas chamadas

- **TestSecurityValidation**: Validações de segurança
  - Não logar credenciais
  - Sanitização de mensagens
  - Não expor internals

- **TestLogConfiguration**: Configuração de logs
  - Nível ERROR
  - Timestamp
  - Traceback de exceções

**Cobertura:** 16 testes para logging seguro

---

### 7. **test_integration.py** - Testes de Integração
- **TestEndToEndPipeline**: Pipeline completo
  - Validar → Analisar → Exportar
  - Detecção de outliers em fluxo real
  - Processamento de grandes datasets (365 dias)
  - Reproducibilidade
  - Tratamento de erros

- **TestReadingStreamProcessing**: Processamento de fluxos
  - Validação sequencial
  - Filtragem de inválidos

**Cobertura:** 11 testes de cenários end-to-end

---

## Configuração

### Requirements de Teste
```bash
pip install -r requirements-test.txt
```

Inclui:
- `pytest==7.4.4` - Framework de testes
- `pytest-cov==4.1.0` - Cobertura de código
- `pytest-timeout==2.2.0` - Timeout em testes
- `pytest-mock==3.12.0` - Mocking tools

### Arquivos de Configuração
- `pytest.ini` - Configuração do pytest (marcadores, paths, etc)
- `conftest.py` - Fixtures compartilhadas (estações, leituras, parâmetros)

---

## Execução de Testes

### Todos os testes
```bash
python -m pytest
# ou
python run_tests.py
```

### Com cobertura de código
```bash
python run_tests.py --coverage
```

Gera relatório HTML em `htmlcov/index.html`

### Testes específicos
```bash
# Por arquivo
python -m pytest tests/test_models.py -v

# Por classe
python -m pytest tests/test_models.py::TestStation -v

# Por função
python -m pytest tests/test_models.py::TestStation::test_station_creation_valid -v

# Com padrão
python -m pytest -k "test_station" -v
```

### Por marcador
```bash
python run_tests.py --unit        # Testes unitários
python run_tests.py --analytics   # Testes de análise
python run_tests.py --database    # Testes de banco de dados
python run_tests.py --marker models  # Marcador customizado
```

### Verbosidade
```bash
python run_tests.py -vv           # Muito verbose
python -m pytest -q               # Quiet (mínimo)
```

---

## Marcadores de Teste

Os seguintes marcadores estão disponíveis:
- `@pytest.mark.unit` - Testes unitários
- `@pytest.mark.integration` - Testes de integração
- `@pytest.mark.database` - Usa banco de dados
- `@pytest.mark.analytics` - Testes de análise
- `@pytest.mark.security` - Testes de segurança
- `@pytest.mark.models` - Testes de modelos

Uso:
```python
@pytest.mark.unit
def test_example():
    pass
```

---

## Estatísticas

**Total de Testes:** 115+

| Módulo | Testes | Escopo |
|--------|--------|--------|
| Models | 20 | Validação de domínio |
| Processing | 14 | Validação de dados |
| Analytics | 30 | Cálculos estatísticos |
| Reporting | 17 | Exportação CSV |
| Database | 17 | Persistência (mock) |
| Security | 16 | Logging e segurança |
| Integration | 11 | Pipelines completos |
| **Total** | **~125** | **Cobertura completa** |

---

## Fixtures Compartilhadas (conftest.py)

Disponíveis em todos os testes:

```python
@pytest.fixture
def sample_station()
    # Station(id=1, code="EST_001", ...)

@pytest.fixture
def sample_reading()
    # Reading com temperature e humidity

@pytest.fixture
def sample_readings_list()
    # 10 leituras para análise

@pytest.fixture
def sample_readings_with_outliers()
    # 12 leituras com outliers óbvios
```

Uso em testes:
```python
def test_example(sample_station, sample_reading):
    assert sample_station.id == 1
    assert len(sample_reading.values) > 0
```

---

## Fluxo de Teste Recomendado

1. **Verificar sintaxe**
   ```bash
   python -m py_compile src/**/*.py
   ```

2. **Rodar testes rápidos**
   ```bash
   python run_tests.py --unit
   ```

3. **Rodar testes de integração**
   ```bash
   python run_tests.py --integration
   ```

4. **Gerar cobertura**
   ```bash
   python run_tests.py --coverage
   ```

5. **Verificar resultados**
   ```bash
   open htmlcov/index.html  # macOS
   start htmlcov/index.html  # Windows
   ```

---

## Notas Importantes

- **Mocks**: Testes de database usam `unittest.mock` (não requer banco real)
- **Determinísticos**: Todos os testes devem produzir mesmos resultados
- **Isolados**: Cada teste é independente (sem side effects)
- **Rápidos**: Suite completa < 5 segundos
- **Descriptivos**: Nomes de testes explicam o que testam

---

## Troubleshooting

### Erro: "No module named 'src'"
```bash
# Adicionar caminho ao Python
cd AcademiaDataScience-Projeto1
python -m pytest tests/
```

### Erro: "ModuleNotFoundError: No module named 'pytest'"
```bash
pip install -r requirements-test.txt
```

### Erro: "pyodbc not found" (testes de database)
- Este erro é esperado - testes usam mocks, não requer real pyodbc

### Testes lentos?
```bash
python -m pytest tests/ -x  # Para no primeiro erro
python -m pytest tests/ --durations=10  # Top 10 mais lentos
```

---

## Próximos Passos

- [ ] Aumentar cobertura para > 80%
- [ ] Adicionar testes de performance
- [ ] CI/CD integration (GitHub Actions)
- [ ] Testes com dados reais do banco
- [ ] Testes de API (quando implementada)
