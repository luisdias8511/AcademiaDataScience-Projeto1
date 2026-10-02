# 🌍 Environmental Monitoring - Data Science Project

**Projeto Prático Integrador**: Pipeline completo de ingestão, processamento, análise e visualização de dados ambientais

## 📋 Visão Geral

Aplicação Python end-to-end para monitorar qualidade da água e dados meteorológicos de múltiplas estações, com:
- ✅ Ingestão automática de APIs (Meersens)
- ✅ ETL com validação e limpeza de dados
- ✅ Armazenamento em SQL Server
- ✅ Análise estatística com detecção de outliers
- ✅ Interface web interativa (Streamlit) e CLI
- ✅ Cobertura de testes de 58%+ (286+ testes)

## 🚀 Quick Start

```bash
# Instalação
pip install -r requirements.txt

# Interface Web
python -m streamlit run examples/streamlit_app.py

# CLI
python -m src.main --cli

# Testes
python tests/run_tests.py --coverage
```

## 📁 Estrutura do Projeto

```
src/
├── main.py                 # Pipeline orquestrador
├── config.py               # Configurações globais
├── analytics/              # Análise estatística
├── database/               # Acesso a dados (SQL Server)
├── ingestion/              # ETL (weather + water)
├── models/                 # Modelos de domínio
├── processing/             # Processamento de dados
├── reporting/              # Exportação (CSV)
├── security/               # Criptografia e logs
└── presentation/           # Streamlit UI
tests/                      # 286+ testes (58% cobertura)
docs/                       # Documentação
```

## 📚 Documentação

- [Architecture](docs/ARCHITECTURE.md) - Design de sistema
- [Setup & Installation](docs/SETUP.md) - Ambiente
- [API Integration](docs/API.md) - Endpoints externos
- [Module Reference](docs/MODULES.md) - Modelos e serviços
- [Tests Guide](tests/README.md) - Como rodar testes

## 🎯 Features

### Core Pipeline
- **Ingestão Paralela**: Weather + Water APIs em simultâneo
- **ETL Robusto**: Validação, normalização, caching
- **Persistência**: SQL Server com ACID compliance
- **Analytics**: Estatísticas avançadas + outlier detection
- **Exportação**: CSV com formatação automática

### User Interface
- **Streamlit Web**: Seleção de estação, intervalo, visualização
- **CLI**: Pipeline de 11 etapas com logging
- **Responsivo**: Download de CSV, múltiplas estações

### Code Quality
- **Type-safe**: Type hints em 100% do código
- **Test Coverage**: 286+ testes (58% cobertura)
- **Security**: Criptografia AES-256, auditoria de logs
- **Performance**: Parallel ingestion, batch operations, caching

## 📊 Statistics Calculated

Por parâmetro:
- **Tendência Central**: Média, Mediana
- **Dispersão**: Desvio Padrão, IQR
- **Anomalias**: Outliers via regra IQR (1.5 × IQR)
- **Distribuição**: Q1, Q3, bounds

## 🗄️ Database Schema

```
Stations ──┐
           ├──> Readings ──> ReadingValues ──> Parameters
           └────────────────────────────────────────┘
```

**Tabelas:**
- Stations: Metadados das estações
- Readings: Dados temporais
- Parameters: Catálogo de parâmetros monitorados
- ReadingValues: Valores medidos

## 🔒 Security

- Chaves API criptografadas em repouso
- Logs com rastreabilidade completa
- Sanitização de URLs sensíveis
- Connection pooling seguro

## 🧪 Testing

```bash
# Todos os testes
python tests/run_tests.py --coverage

# Por marcador
python tests/run_tests.py --unit
python tests/run_tests.py --integration
python tests/run_tests.py --database
python tests/run_tests.py --analytics
```

**Estatísticas:**
- 286+ testes
- 58% cobertura geral
- 100% ETL water
- 96% ETL weather
- 95% main.py
- 3s tempo total de execução

## 📝 Logging

Logs estruturados em `logs/app.log`:
- INFO: Operações normais
- WARNING: Situações anômalas
- ERROR: Erros com contexto completo
- DEBUG: Detalhes técnicos

## 🛠️ Technology Stack

| Camada | Tecnologia |
|--------|-----------|
| Language | Python 3.14.7 |
| Data | pandas, Decimal |
| Database | SQL Server (pyodbc) |
| APIs | requests |
| UI | Streamlit |
| Testing | pytest (286+ testes) |
| Security | cryptography |

## 📖 Development

Leia [SETUP.md](docs/SETUP.md) para ambiente local.

Principais arquivos para customização:
- `src/config.py` - Configurações globais
- `src/constants.py` - Constantes da aplicação
- `sql/CREATE_TABLES.sql` - Schema do banco

## 📄 License

Projeto acadêmico

## 🤝 Contributing

1. Fork repository
2. Create feature branch
3. Add tests
4. Ensure 58%+ coverage
5. Submit PR

## 📞 Support

Consulte `logs/app.log` para detalhes de erros.

Documentação técnica: [docs/](docs/) folder.