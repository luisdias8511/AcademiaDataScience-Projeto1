/*
========================================================
BANCO: EnvironmentalMonitoring
========================================================
*/
IF NOT EXISTS (
    SELECT *
    FROM sys.databases
    WHERE name = 'EnvironmentalMonitoring'
)
BEGIN
    CREATE DATABASE EnvironmentalMonitoring;
END
GO
USE EnvironmentalMonitoring;
GO