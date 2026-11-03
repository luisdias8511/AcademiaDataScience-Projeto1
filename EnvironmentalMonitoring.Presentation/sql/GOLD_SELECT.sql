SELECT
    ds.StationCode,
    dp.CategoryCode,
    dp.ParameterCode,
    dp.ParameterName,

    fm.MeasurementDateTime,
    fm.MeasuredValue,
    fm.MovingAverageValue,

    fm.ZScore,
    fm.IqrLowerBound,
    fm.IqrUpperBound,

    fm.IsOutlier,
    fm.OutlierMethod

FROM gold.FactMeasurements fm

INNER JOIN gold.DimStation ds
    ON ds.StationKey = fm.StationKey

INNER JOIN gold.DimParameter dp
    ON dp.ParameterKey = fm.ParameterKey

ORDER BY
    ds.StationCode,
    dp.ParameterCode,
    fm.MeasurementDateTime;
GO