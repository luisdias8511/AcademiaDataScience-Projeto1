USE EnvironmentalMonitoring;
GO

SET NOCOUNT ON;
SET XACT_ABORT ON;
GO

BEGIN TRY
    BEGIN TRANSACTION;

    /* ============================================================
       DIM STATION
       ============================================================ */

    INSERT INTO gold.DimStation
    (
        StationId,
        StationCode,
        StationName,
        Latitude,
        Longitude,
        Municipality,
        State,
        Country
    )
    SELECT
        s.Id,
        s.Code,
        s.Name,
        s.Latitude,
        s.Longitude,
        s.Municipality,
        s.State,
        s.Country
    FROM dbo.Stations s
    WHERE NOT EXISTS
    (
        SELECT 1
        FROM gold.DimStation ds
        WHERE ds.StationId = s.Id
    );

    /* ============================================================
       DIM PARAMETER
       ============================================================ */

    INSERT INTO gold.DimParameter
    (
        ParameterId,
        ParameterCode,
        ParameterApiCode,
        ParameterName,
        Unit,
        CategoryId,
        CategoryCode,
        CategoryName
    )
    SELECT
        p.Id,
        p.Code,
        p.CodeApi,
        p.Name,
        p.Unit,
        pc.Id,
        pc.Code,
        pc.Name
    FROM dbo.Parameters p
    INNER JOIN dbo.ParameterCategories pc
        ON pc.Id = p.CategoryId
    WHERE NOT EXISTS
    (
        SELECT 1
        FROM gold.DimParameter dp
        WHERE dp.ParameterId = p.Id
    );

    COMMIT TRANSACTION;

END TRY
BEGIN CATCH

    IF @@TRANCOUNT > 0
        ROLLBACK TRANSACTION;

    THROW;

END CATCH;
GO