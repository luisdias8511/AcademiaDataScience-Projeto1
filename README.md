# AcademiaDataScience-Projeto1
Academia Data Science - Projeto 1

Projeto Prático Integrador: Pipeline de Monitoramento e Análise de Dados Ambientais

Objetivo Geral

Desenvolver uma aplicação completa em Python para capturar, tratar, analisar, persistir e disponibilizar dados de estações de monitoramento ambiental (qualidade da água e dados meteorológicos), aplicando boas práticas de código, segurança, estatística e controle de versão.


=============================================
Escopo do MVP
=============================================
 
Fonte de Dados 

    Ingestão JSON da API (ou arquivo JSON) 
        https://open-meteo.com 

            https://api.open-meteo.com/v1/forecast?latitude=-23.5475&longitude=-46.63611  

            https://partners.meersens.com/ 
 

    Validação e limpeza de dados; 

    Anominazação; 
    
    Persistência Banco SQL Server 
    com quatro tabelas:  
        Stations (metadados das estações) 
        ID Code Name Latitude Longitude  

        Readings (dados temporais) 
        DateTime StationId  

        Parameters (parâmetros de monitoramento)
        ID Code Name Unit

        ReadingValues (valores de leitura)
        ID ReadingId ParameterId Value 
 
    Consulta SQL 

    Analise estatistica: 
        Tendência central: Média e Mediana. 
        Dispersão: Desvio Padrão e Intervalo Interquartil. 
        Identificar registros anômalos (outliers) utilizando a regra do amplitude interquartil (IQR). 

    Relatório no terminal OU Textual 

=============================================
Retorno das APIs
=============================================

API Weather
            "parameters": { 

                "apparent_temperature": { 

                    "name": "Apparent temperature",                     

                    "value": 21.06, 

                    "unit": "°C",                  

                }, 

                "cloud_cover": { 

                    "name": "Cloud cover",               

                    "value": 97, 

                    "unit": "%",                     

                }, 

                "humidity": { 

                    "name": "Humidity",                   

                    "value": 64.37, 

                    "unit": "%",                  

 

                }, 

                "precipitations": {                   

                    "name": "Precipitations",               

 

                    "unit": "mm", 

                    "value": 0,                    

                }, 

                "pressure": {                   

                    "name": "Pressure",                    

                    "value": 972.82, 

                    "unit": "hPa",                   

                }, 

                "temperature": {                    

                    "name": "Temperature",                     

                    "value": 21.06, 

                    "unit": "°C",                

                }, 

                "wind_direction": {                    

                    "name": "Wind direction",   

                    "value": 252.99, 

                    "unit": "°",                 

 

                }, 

                "wind_speed": { 

                    "name": "Wind speed", 

                    "value": 8.99, 

                    "unit": "km/h",                 

                } 

} 


WATER:

"pollutants": {     
    "pH": { 
        "name": "pH", 
        "unit": "", 
        "value": 7.4, 
        }, 

} 

=============================================
DER
=============================================

┌────────────────────────┐
│      STATIONS          
├────────────────────────┤
│ Id (PK)                
│ Code                   
│ Name                   
│ Latitude               
│ Longitude              
└────────────┬───────────┘
             │
             │ 1:N
             │
┌────────────▼───────────┐
│      READINGS          
├────────────────────────┤
│ Id (PK)                
│ StationId (FK)         
│ DateTime               
└────────────┬───────────┘
             │
             │ 1:N
             │
┌────────────▼───────────┐
│   READINGVALUES        
├────────────────────────┤
│ Id (PK)                
│ ReadingId (FK)         
│ ParameterId (FK)       
│ Value                  
└────────────┬───────────
             │
             │ N:1
             │
┌────────────▼───────────┐
│      PARAMETERS        
├────────────────────────┤
│ Id (PK)                
│ Code                   
│ Name                   
│ Unit                   
└────────────────────────┘

========================================================
Estrutura Inicial do repositório:
========================================================

AcademiaDataScience-Projeto1/
├── .github/
├── data/
│   ├── raw/
│   └── processed/
├── database/
├── docs/
│   ├── architecture.md
│   ├── data_dictionary.md
├── reports/
├── sql/
│   ├── ANALYTICAL_QUERIES.sql
│   └── CREATE_DATABASE.sql
│   └── CREATE_TABLES.sql
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── ingestion/
│   │   ├── __init__.py
│   ├── processing/
│   │   ├── __init__.py
│   ├── database/
│   │   ├── __init__.py
│   ├── analytics/
│   │   ├── __init__.py
│   └── reporting/
│       ├── __init__.py
├── tests/
│   ├── fixtures/
├── .env.example
├── .gitignore
├── pyproject.toml
├── requirements.txt
└── README.md