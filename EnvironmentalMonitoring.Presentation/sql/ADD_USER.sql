USE EnvironmentalMonitoring;
GO

CREATE USER environment_api
FOR LOGIN environment_api;

-- Adiciona o usuário à role de leitura (SELECT)
ALTER ROLE [db_datareader] ADD MEMBER environment_api;
GO

-- Adiciona o usuário à role de escrita (INSERT, UPDATE, DELETE)
ALTER ROLE [db_datawriter] ADD MEMBER environment_api;
GO
