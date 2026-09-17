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
    pelo menos duas tabelas:  
        estacoes (metadados das estações) 
        ID Código Nome Latitude Longitude  

    leituras (dados temporais) 
        data_hora_medicao 
        Temperatura 
 
    Consulta SQL 

    Analise estatistica: 
        Tendência central: Média e Mediana. 
        Dispersão: Desvio Padrão e Intervalo Interquartil. 
        Identificar registros anômalos (outliers) utilizando a regra do amplitude interquartil (IQR). 

    Relatório no terminal OU Textual 



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


DER
======

┌────────────────────────┐
│     ESTACOES           
├────────────────────────┤
│ id (PK)                
│ codigo                 
│ nome                   
│ latitude               
│ longitude              
└────────────┬───────────┘
             │
             │ 1:N
             │
┌────────────▼───────────┐
│      LEITURAS          
├────────────────────────┤
│ id (PK)                
│ estacao_id (FK)        
│ data_hora              
└────────────┬───────────┘
             │
             │ 1:N
             │
┌────────────▼───────────┐
│   VALORES_LEITURA      
├────────────────────────┤
│ id (PK)                			
│ leitura_id (FK)        
│ parametro_id (FK)      
│ valor                  
└────────────┬───────────
             │
             │ N:1
             │
┌────────────▼───────────┐
│      PARAMETROS        
├────────────────────────┤
│ id (PK)                
│ codigo                 
│ nome                  
│ unidade        
└────────────────────────┘





Dia 1: Kickoff e alinhamento 
Definir objetivo e escopo do MVP 
Selecionar APIs 

 

Dia 2: 
Criar repositório 
Criar quadro de trabalho 
Criar primeira versão do modelo de dados 

